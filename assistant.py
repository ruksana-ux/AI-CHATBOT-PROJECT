"""Customer Support Assistant core logic.
Strictly adheres to:
1. Customer Query Handling (LLM response, conversation history, clarifying questions for ambiguity)
2. FAQ Assistant (grounded in faqs.json, admits unavailable information, no invented policies)
3. Order Status Checker (validates order number and customer identity, calls Python function)
Uses Ollama or Hugging Face Transformers. No LangChain.
"""
import re
import json
from typing import List, Dict, Tuple, Optional, Any
from tools import load_faqs, check_order_status
from llm_engine import get_llm, OllamaModel, HuggingFaceTransformersModel


def build_system_prompt() -> str:
    """Build the system prompt containing company FAQs and behavioral guidelines."""
    faqs = load_faqs()
    return f"""You are an AI Customer Support Assistant for an online retail store.

You must strictly adhere to the following rules:

1. CUSTOMER QUERY HANDLING:
- Be polite, professional, and helpful.
- Maintain conversation context across turns.
- If a customer's request is ambiguous or lacks necessary details, ask a polite clarifying question.

2. FAQ POLICIES (GROUNDING):
- Answer questions regarding shipping, returns, refunds, and product policies using ONLY the official company FAQs provided below.
- Do NOT invent or assume any policies, timelines, or rules.
- If the required information is not found in the FAQs, you must explicitly admit that the information is unavailable in our store policies and suggest contacting customer support.

3. ORDER STATUS CHECKER:
- When a customer asks about an order, you must validate BOTH the order number (e.g., ORD1002) and customer identity (the customer's email address).
- Never disclose order details without customer identity verification.
- If verified order information is provided to you in the prompt, explain the order status, estimated delivery date, and product details clearly.

COMPANY FAQS (JSON):
{json.dumps(faqs, indent=2)}
"""


class CustomerSupportAssistant:
    """Core AI Customer Support Assistant."""

    def __init__(self, llm=None):
        self.llm = llm or get_llm()
        self.system_prompt = build_system_prompt()

    @staticmethod
    def extract_order_id(text: str) -> Optional[str]:
        """Extract order number matching pattern ORD#### or similar."""
        match = re.search(r'\b(ORD\d{3,5})\b', text, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return None

    @staticmethod
    def extract_email(text: str) -> Optional[str]:
        """Extract email address from text."""
        match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if match:
            return match.group(0).lower()
        return None

    def find_order_details_in_history(self, history: List[Dict[str, str]], current_message: str) -> Tuple[Optional[str], Optional[str]]:
        """Look through current message and session history for order_id and email."""
        order_id = self.extract_order_id(current_message)
        email = self.extract_email(current_message)

        # Check previous user turns if not found in current message
        if not order_id or not email:
            for turn in reversed(history):
                if turn.get("role") == "user":
                    content = turn.get("content", "")
                    if not order_id:
                        order_id = self.extract_order_id(content)
                    if not email:
                        email = self.extract_email(content)
                if order_id and email:
                    break

        return order_id, email

    def _is_order_query(self, message: str) -> bool:
        """Detect if the customer message is related to checking an order."""
        keywords = ["order", "ord", "track", "package", "delivery status", "where is my", "shipment"]
        lower = message.lower()
        return any(k in lower for k in keywords)

    def _rule_based_fallback(self, user_message: str, history: List[Dict[str, str]], order_id: Optional[str] = None, email: Optional[str] = None) -> str:
        """
        Fallback response generator if LLM server is temporarily unreachable,
        ensuring strict FAQ adherence, order verification, and ambiguity handling.
        """
        lower = user_message.lower().strip()

        # Check if asking for order status
        if self._is_order_query(user_message) or order_id or email:
            if not order_id and not email:
                return "I would be happy to check your order status! Please provide your order number (e.g., ORD1002) and the email address associated with your order."
            if order_id and not email:
                return f"I found order {order_id}. To protect your privacy and verify your identity, could you please provide the email address used for this order?"
            if email and not order_id:
                return f"Thank you for providing your email ({email}). Please provide your order number (e.g., ORD1002) so I can retrieve your order status."
            
            # Both provided: call Python function
            result = check_order_status(order_id, email)
            if result.get("success"):
                return (
                    f"Here are the details for your order **{result['order_id']}**:\n"
                    f"- **Customer**: {result['customer_name']}\n"
                    f"- **Product**: {result['product']} (Qty: {result['quantity']})\n"
                    f"- **Status**: {result['status']}\n"
                    f"- **Estimated Delivery**: {result['estimated_delivery']}\n\n"
                    "Please let me know if you need anything else!"
                )
            else:
                return f"Verification notice: {result.get('error', 'Could not verify order details.')} Please double-check your order number and email."

        # Check FAQs
        faqs = load_faqs()
        for item in faqs:
            q_keywords = [w for w in item["question"].lower().replace("?", "").split() if len(w) > 3]
            match_count = sum(1 for w in q_keywords if w in lower)
            if match_count >= 2 or item["category"] in lower:
                # If specific category matches
                if "shipping" in lower and item["category"] == "shipping":
                    if "international" in lower and "international" in item["question"].lower():
                        return item["answer"]
                    if "how long" in lower or "time" in lower or "take" in lower:
                        return item["answer"]
                elif "return" in lower and item["category"] == "returns":
                    return item["answer"]
                elif "refund" in lower and item["category"] == "refunds":
                    return item["answer"]
                elif "warranty" in lower and "warranty" in item["question"].lower():
                    return item["answer"]
                elif "cancel" in lower and "cancel" in item["question"].lower():
                    return item["answer"]

        # Ambiguous query check
        if len(lower.split()) <= 3 or lower in ["help", "hello", "hi", "support", "issue"]:
            return "Hello! I am your AI Customer Support Assistant. How can I help you today? You can ask about our shipping policies, returns, refunds, product warranties, or check an order status."

        # If question is asking about store policies not in FAQs -> admit unavailable
        policy_triggers = ["discount", "coupon", "gift card", "price match", "in-store", "pickup", "membership", "installment"]
        if any(pt in lower for pt in policy_triggers) or "do you" in lower or "what is" in lower:
            return "I do not have information regarding that policy in our official store records. Please contact our human support team at support@example.com for further assistance."

        return "Could you please clarify your question? Let me know if you need help with shipping, returns, refunds, product policies, or checking an order status."

    def respond(self, user_input: str, media_urls: Optional[List[str]] = None, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Respond to customer query and optional media attachments (images/videos).
        Returns a structured dictionary response for APIs.
        """
        # 1. First, check if there is an image/video attached
        if media_urls:
            # Handle media processing (e.g., save to a database, or analyze using a Vision model)
            return {
                "type": "media_received",
                "message": f"Thank you for sharing the media file(s). Our support team has received the {len(media_urls)} attachment(s) and is reviewing your request."
            }

        # 2. Existing text processing flows
        history = history or []
        answer = self.process_message(user_input, history)
        return {
            "type": "text_response",
            "message": answer
        }

    def process_message(self, user_message: str, history: List[Dict[str, str]], media_urls: Optional[List[str]] = None) -> str:
        """
        Main query processing method:
        1. Checks for media attachments (e.g., images of damaged products).
        2. Checks order status verification logic (calls Python function if validated).
        3. Injects FAQ and context into LLM.
        4. Returns LLM response or graceful fallback.
        """
        if media_urls:
            return f"Thank you for sharing the media file(s). Our support team has received the {len(media_urls)} attachment(s) and is reviewing your request."

        order_id, email = self.find_order_details_in_history(history, user_message)

        # Check if this is an order status check request
        is_order_intent = self._is_order_query(user_message) or (order_id is not None)

        tool_result_context = ""
        if is_order_intent:
            if order_id and not email:
                # Identity not verified yet - must ask for customer identity
                return f"I can help you check the status of order {order_id}! To verify your identity and protect your privacy, could you please provide the email address used when placing this order?"
            elif not order_id and email:
                return f"Thank you for providing your email ({email}). Could you please share your order number (e.g., ORD1002) so I can look up your order details?"
            elif order_id and email:
                # Both present -> execute the Python tool
                tool_data = check_order_status(order_id, email)
                tool_result_context = (
                    f"\n[SYSTEM TOOL RESULT for check_order_status(order_id='{order_id}', email='{email}')]:\n"
                    f"{json.dumps(tool_data, indent=2)}\n"
                    "INSTRUCTION: Explain the above order result to the customer in a warm, professional customer support manner."
                )

        # Build message history for LLM
        messages = [{"role": "system", "content": self.system_prompt}]

        for turn in history:
            messages.append({"role": turn["role"], "content": turn["content"]})

        current_content = user_message
        if tool_result_context:
            current_content += f"\n\n{tool_result_context}"

        messages.append({"role": "user", "content": current_content})

        # Generate response using Ollama or Hugging Face Transformers
        try:
            response = self.llm.generate(messages)
            if response and response.strip():
                return response.strip()
        except Exception as e:
            # If the selected local model or inference endpoint is not running/available,
            # execute rule-grounded fallback to ensure uninterrupted operation.
            print(f"[Assistant] LLM generation note: {e}")
            return self._rule_based_fallback(user_message, history, order_id, email)

        return self._rule_based_fallback(user_message, history, order_id, email)


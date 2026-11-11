"""Automated test suite verifying all guidelines."""
from assistant import CustomerSupportAssistant
from tools import check_order_status, load_faqs, load_orders


def test_faq_loading():
    faqs = load_faqs()
    assert len(faqs) >= 6, "Expected at least 6 FAQ items"
    categories = {f["category"] for f in faqs}
    assert "shipping" in categories
    assert "returns" in categories
    assert "refunds" in categories
    assert "product policies" in categories
    print("[PASS] test_faq_loading")


def test_order_status_checker():
    # 1. Valid order number and matching email
    res1 = check_order_status("ORD1002", "ravi@example.com")
    assert res1["success"] is True
    assert res1["order_id"] == "ORD1002"
    assert res1["status"] == "Shipped"
    assert res1["product"] == "Smart Watch Series 4"
    assert res1["estimated_delivery"] == "2026-11-02"

    # 2. Identity validation failure: wrong email
    res2 = check_order_status("ORD1002", "wrong@example.com")
    assert res2["success"] is False
    assert "failed" in res2["error"].lower()

    # 3. Missing order ID
    res3 = check_order_status("", "ravi@example.com")
    assert res3["success"] is False
    assert "missing order number" in res3["error"].lower()

    # 4. Missing email identity
    res4 = check_order_status("ORD1002", "")
    assert res4["success"] is False
    assert "missing customer identity" in res4["error"].lower()

    # 5. Non-existent order
    res5 = check_order_status("ORD9999", "user@example.com")
    assert res5["success"] is False
    assert "no order found" in res5["error"].lower()

    print("[PASS] test_order_status_checker")


def test_customer_query_and_faq_grounding():
    assistant = CustomerSupportAssistant()

    # FAQ check
    ans_shipping = assistant.process_message("How long does shipping take?", [])
    assert "5-7 business days" in ans_shipping

    # Uninvented policy check (must admit unavailable)
    ans_unavailable = assistant.process_message("Do you offer student discounts?", [])
    assert "do not have information" in ans_unavailable.lower() or "support" in ans_unavailable.lower()

    # Ambiguity check
    ans_ambiguous = assistant.process_message("help", [])
    assert "how can i help" in ans_ambiguous.lower() or "clarify" in ans_ambiguous.lower()

    print("[PASS] test_customer_query_and_faq_grounding")


def test_multi_turn_order_verification_flow():
    assistant = CustomerSupportAssistant()
    history = []

    # Turn 1: Customer asks about order without email
    msg1 = "Where is my order ORD1002?"
    reply1 = assistant.process_message(msg1, history)
    assert "ORD1002" in reply1
    assert "email" in reply1.lower() or "identity" in reply1.lower()

    history.append({"role": "user", "content": msg1})
    history.append({"role": "assistant", "content": reply1})

    # Turn 2: Customer provides email to complete verification
    msg2 = "ravi@example.com"
    reply2 = assistant.process_message(msg2, history)
    assert "ORD1002" in reply2
    assert "Shipped" in reply2
    assert "Smart Watch" in reply2

    print("[PASS] test_multi_turn_order_verification_flow")


def test_media_support():
    assistant = CustomerSupportAssistant()
    # Test respond with media_urls
    res = assistant.respond("My item arrived damaged", media_urls=["https://example.com/damaged.jpg"])
    assert res["type"] == "media_received"
    assert "1 attachment" in res["message"]

    # Test respond with plain text
    res_text = assistant.respond("What is your return policy?")
    assert res_text["type"] == "text_response"
    assert "30 days" in res_text["message"] or "return" in res_text["message"].lower()

    print("[PASS] test_media_support")


if __name__ == "__main__":
    test_faq_loading()
    test_order_status_checker()
    test_customer_query_and_faq_grounding()
    test_multi_turn_order_verification_flow()
    test_media_support()
    print("\nALL TESTS PASSED SUCCESSFULLY!")

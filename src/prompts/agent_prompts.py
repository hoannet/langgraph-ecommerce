"""Agent-specific prompt templates."""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Intent Classification Prompt
INTENT_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        (
            "human",
            """Analyze this user message and classify the intent:

User message: {user_message}

Available intents:

1. product_search - User wants to SEARCH/BROWSE/VIEW products
   ✅ YES: "Show me X", "I want to buy X", "What products", "Search for X", "Do you have X"
   ❌ NOT: "I want product prod_001" (that's order), "Pay" (that's payment)
   Examples: "Show me laptops", "Show me iPhone", "What products do you have?"

2. order - User wants to ORDER a SPECIFIC product (has product ID or number)
   ✅ YES: "I want product prod_001", "Order product X", "I'll take #1"
   ❌ NOT: "Show me products" (that's search), "Pay" (that's payment)
   Examples: "I want product prod_001", "Order this laptop", "I'll take 2"

3. payment - User wants to PAY/MAKE PAYMENT (must have "pay" keyword!)
   ✅ YES: "Pay", "Pay now", "I want to pay", "Process payment", "Charge me"
   ❌ NOT: "Show me" (that's search), "I want product" (that's order)
   Examples: "Pay now", "I want to pay", "Process payment for $50"

4. faq - Questions about services/policies
   Examples: "What are your hours?", "How does shipping work?"

5. general - Greetings, thank you, casual chat
   Examples: "Hello", "Thank you", "How are you?"

6. escalation - Need human support
   Examples: "I need a manager", "This is urgent"

CRITICAL DECISION RULES:
1. Does message contain "show me", "search", "what products", "do you have"? → product_search
2. Does message contain "I want product [ID]", "order product"? → order  
3. Does message contain "pay", "payment", "charge"? → payment
4. If NONE of above → general or faq

IMPORTANT: "Show me X" is ALWAYS product_search, NEVER payment!

Respond in JSON format with lowercase intent values:
{{
    "intent": "product_search|order|payment|faq|general|escalation",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}

IMPORTANT: Use lowercase for intent value (e.g., "product_search" not "PRODUCT_SEARCH")""",
        ),
    ]
)

# Payment Extraction Prompt
PAYMENT_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        (
            "human",
            """Extract payment information from this user message:

User message: {user_message}

Extract the amount and currency. If currency is not specified, default to USD.

Respond in JSON format:
{{
    "amount": <number>,
    "currency": "<currency_code>",
    "description": "<optional description>"
}}

Examples:
- "I want to pay $50" -> {{"amount": 50.0, "currency": "USD"}}
- "Pay 100 EUR" -> {{"amount": 100.0, "currency": "EUR"}}
- "Charge me 25.99" -> {{"amount": 25.99, "currency": "USD"}}
- "I need to pay $30 for subscription" -> {{"amount": 30.0, "currency": "USD", "description": "subscription"}}

IMPORTANT: Return valid JSON only, no additional text.""",
        ),
    ]
)

# Payment Processing Prompt
PAYMENT_PROCESSING_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        (
            "human",
            """Process this payment request:

Amount: {amount}
Currency: {currency}
Description: {description}

Validate the information and provide a response about the payment status.
Be clear and professional.""",
        ),
    ]

)

# FAQ Response Prompt
FAQ_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        (
            "human",
            """Answer this FAQ question:

Question: {question}

Provide a clear, concise, and helpful answer.""",
        ),
    ]
)

# Escalation Prompt
ESCALATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        (
            "human",
            """Handle this escalation case:

User message: {user_message}
Context: {context}

Acknowledge the issue, collect necessary information, and set expectations.""",
        ),
    ]
)

# General Conversation Prompt
CONVERSATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "{system_prompt}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{user_message}"),
    ]
)

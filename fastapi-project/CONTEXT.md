# Triage

Customer-facing chatbot that holds a conversation with a customer while
continuously working out what they actually need, so the request can be routed
to whoever (or whatever) should handle it.

## Language

**Customer Request**:
The underlying problem a customer wants solved. It persists across the whole
conversation — many messages describe one request.
_Avoid_: ticket, issue, query, case

**Triage**:
The chatbot's current assessment of a Customer Request. Produced fresh on every
turn and expected to change as the conversation reveals more; it is never final.
_Avoid_: classification, verdict, label

**Request Category**:
Which area of the business a Customer Request belongs to. Drawn from a fixed,
closed set — the chatbot may not invent new ones.
_Avoid_: type, topic, intent, tag

**Conversation**:
One customer's continuous exchange with the chatbot about a single Customer
Request. Survives across HTTP requests.
_Avoid_: session, chat, thread

**Reply**:
The customer-facing text the chatbot says back on a turn. Carried alongside the
Triage, not derived from it.
_Avoid_: message, answer, response

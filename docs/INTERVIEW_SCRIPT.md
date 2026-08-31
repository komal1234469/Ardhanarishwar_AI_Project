# Interview Script — "What problem are you solving?"

## English (verbatim, ready to speak)

"Our platform focuses on two major problems. First is the candidate problem. Many students
have theoretical education but lack the practical skills required by industry, which creates
a gap between university education and company requirements. Our AI analyzes a candidate's
profile, career goal and target role, identifies skill gaps, recommends practical projects,
learning paths and suitable companies, and prepares the candidate for the required role.

We also extend this to unskilled or first-time job seekers — people without a formal
education background. For them, the platform doesn't do gap analysis against an advanced
role; instead it breaks a target skill down into small, practical, step-by-step training,
so they can become job-ready from scratch.

Second is the business and client problem. A business owner can submit a real-world business
problem to our platform. Our GenAI system first tries to solve it using our knowledge base
and contextual information. If the AI cannot provide a reliable, confident answer, the
request is escalated to our human team, who respond within 24 hours.

So the main idea is AI-first assistance with human support when necessary, while using
Generative AI to provide personalized and context-aware solutions — for both skilled and
unskilled candidates, and for businesses of any size."

## Follow-up: "How is this different from a normal chatbot?"

"A normal chatbot gives a fixed or generic answer regardless of confidence. Ours does three
things differently: it uses RAG to ground answers in our actual knowledge base instead of
inventing them; it tailors the response depth and learning path to whether the candidate is
skilled or unskilled; and most importantly, when its retrieval confidence is low, it doesn't
guess — it escalates the question to a human expert with a 24-hour response commitment. That
escalation queue is visible in our Admin dashboard right now in the prototype."

## Follow-up: "How would this work at a global scale?"

"The architecture doesn't change — only the scale of two things grows: the knowledge base
(multilingual, region-specific job market data) and the human escalation desk, which in
production would route tickets to a distributed team across time zones so the 24-hour
response commitment holds everywhere, not just in one country."

## Hinglish (short version, casual explanation)

"Humara platform do problems solve karta hai. Ek, candidates ka — chahe woh skilled ho ya
bilkul unskilled/first-time job seeker, dono ke liye alag learning path deta hai: skilled ke
liye gap-analysis aur better opportunities, unskilled ke liye step-by-step foundational
training. Doosra, business owners ka — woh apna real problem (jaise sales kam ho rahi hain)
platform par daal sakte hain, AI pehle try karta hai solve karne ka, aur agar AI confident
nahi hai to woh query human expert team ko forward ho jaati hai jo 24 ghante mein reply karti
hai. Matlab AI-first, lekin jab AI ko pata nahi hota, wahan human backup hai — guess nahi
karta."

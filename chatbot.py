from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)


def build_system_prompt(profile: dict | None, recommendations: list | None) -> str:
    base = """You are Career Compass, a friendly and knowledgeable AI career advisor.
You help users understand their career options, skill gaps, and learning paths.
Keep responses concise, warm, and actionable — ideally 2-4 sentences unless the user asks for more detail.
"""
    if profile:
        skills = ", ".join(profile.get("skills", {}).get("technical", [])[:15]) or "not yet analysed"
        soft   = ", ".join(profile.get("skills", {}).get("soft", [])[:8]) or "none detected"
        name   = profile.get("name") or "the user"
        edu    = profile.get("education", [])
        edu_str = edu[0] if edu else "not specified"

        base += f"""
The user's name is {name}.
Their technical skills include: {skills}.
Their soft skills include: {soft}.
Their education: {edu_str}.
"""
    if recommendations:
        top = [f"{r['career']} ({r['score']}%)" for r in recommendations[:5]]
        base += f"Their top career matches are: {', '.join(top)}.\n"

    base += "\nUse this context to give personalised advice. If you don't have profile context yet, still help with general career questions."
    return base


def get_response(
    user_message: str,
    chat_history: list,
    profile: dict | None = None,
    recommendations: list | None = None
) -> str:
    """
    user_message   : the latest message from the user
    chat_history   : list of {"role": "user"/"assistant", "content": "..."} dicts
    profile        : parsed resume profile dict (can be None)
    recommendations: list of career match dicts (can be None)
    """
    system_prompt = build_system_prompt(profile, recommendations)

    messages = [{"role": "system", "content": system_prompt}]

    # include last 10 turns of history to keep context without blowing token limit
    for turn in chat_history[-10:]:
        messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # fast, free-tier Groq model
            messages=messages,
            temperature=0.7,
            max_tokens=512,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Sorry, I'm having trouble connecting right now. ({str(e)})"

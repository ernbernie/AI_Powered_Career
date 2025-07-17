import logging
import textwrap

MAX_RESUME_CHARS = 3000  # hard cap to keep the prompt reasonable

def build_career_roadmap_prompt(goal: str, location: str, resume_text: str | None = None) -> str:
    logging.info("Building roadmap prompt…")

    chunks: list[str] = [
        textwrap.dedent(f"""
            You are a realistic and encouraging expert career strategist.
            Your task is to create a 5‑year career roadmap **in JSON only**.

            Context:
            - User's 5‑year goal: "{goal}"
            - User's location:   "{location}"
        """).strip()
    ]

    if resume_text:
        # Escape triple quotes to prevent issues
        safe_resume = resume_text.replace('"""', '\\"""')
        resume_chunk = textwrap.indent(safe_resume, "    ")
        chunks.append(
            "- User's resume:\n" +
            resume_chunk
        )

    chunks.append(textwrap.dedent("""
        Instructions:
        1. Rearticulate the user's goal…
        2. Working backwards from Year 5…
        3. For Year 1 add four quarterly SMART goals.
        4. Return **only** valid JSON in exactly this schema:
        {
          "five_year_goal": "...",
          "location": "...",
          "yearly_goals": [
            {"year": 5, "year_goal": "..."},
            {"year": 4, "year_goal": "..."},
            {"year": 3, "year_goal": "..."},
            {"year": 2, "year_goal": "..."},
            {
              "year": 1,
              "year_goal": "...",
              "quarterly_smart_goals": [
                {"quarter": "Q1", "goal": "..."},
                {"quarter": "Q2", "goal": "..."},
                {"quarter": "Q3", "goal": "..."},
                {"quarter": "Q4", "goal": "..."}
              ]
            }
          ]
        }

        Rules:
        - JSON only, no markdown or prose.
        - Make every goal concrete, actionable, realistic.
        - Use the location and resume details wherever helpful.
    """).strip())

    prompt = "\n\n".join(chunks)
    logging.info("Prompt built successfully.")
    return prompt
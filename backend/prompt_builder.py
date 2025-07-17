# backend/prompt_builder.py
import logging
import textwrap

MAX_RESUME_CHARS = 3000  # hard cap to keep the prompt ≤ GPT-4 limits

def build_career_roadmap_prompt(goal: str, location: str, resume_text: str | None = None) -> str:
    logging.info("Building roadmap prompt…")

    chunks: list[str] = [
        textwrap.dedent(f"""
            You are **Strat-AI**, an elite, data-driven career strategist. Your sole function is to perform a rigorous gap analysis between a user's resume and their stated goal. You are meticulous and hyper-realistic. Every single goal you propose must be directly justified by a specific detail from the user's resume and location. You do not give generic advice.

            Context:
            - User's 5‑year goal: "{goal}"
            - User's location:   "{location}"
        """).strip()
    ]

    if resume_text:
        # Escape triple quotes to prevent f-string issues
        safe_resume = resume_text.replace('"""', '\\"""')
        resume_chunk = textwrap.indent(safe_resume, "    ")
        chunks.append(
            "- User's resume:\n" +
            resume_chunk
        )

    # Updated instructions with new JSON schema including SMART breakdown
    chunks.append(textwrap.dedent("""
        Instructions:
        1. Analyze and Identify Gaps: First, scrutinize the user's resume and identify the top 3-5 critical skill, certification, or experience gaps between their current state and their 5-year goal.
        2. Plan Backwards to Close Gaps: Plan backwards from Year 5. Each `year_goal` must be a logical milestone that explicitly closes one of the gaps you identified.
        3. Justify Year 1 Quarterly Goals: For Year 1, create exactly four distinct quarterly goals. Each `goal` must provide a brief summary, and include a detailed SMART breakdown.
        4. JSON Schema: Return **only** valid JSON matching this structure:
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
                {
                  "quarter": "Q1",
                  "goal": "A brief summary of the quarterly goal.",
                  "smart": {
                    "S": "Specific: A detailed explanation of the specific task.",
                    "M": "Measurable: How progress will be measured.",
                    "A": "Achievable: Why this goal is achievable.",
                    "R": "Relevant: How this goal is relevant to the 5-year plan.",
                    "T": "Time-bound: The specific deadline for this goal."
                  }
                },
                {
                  "quarter": "Q2",
                  "goal": "A brief summary of the quarterly goal.",
                  "smart": {
                    "S": "Specific: A detailed explanation of the specific task.",
                    "M": "Measurable: How progress will be measured.",
                    "A": "Achievable: Why this goal is achievable.",
                    "R": "Relevant: How this goal is relevant to the 5-year plan.",
                    "T": "Time-bound: The specific deadline for this goal."
                  }
                },
                {
                  "quarter": "Q3",
                  "goal": "A brief summary of the quarterly goal.",
                  "smart": {
                    "S": "Specific: A detailed explanation of the specific task.",
                    "M": "Measurable: How progress will be measured.",
                    "A": "Achievable: Why this goal is achievable.",
                    "R": "Relevant: How this goal is relevant to the 5-year plan.",
                    "T": "Time-bound: The specific deadline for this goal."
                  }
                },
                {
                  "quarter": "Q4",
                  "goal": "A brief summary of the quarterly goal.",
                  "smart": {
                    "S": "Specific: A detailed explanation of the specific task.",
                    "M": "Measurable: How progress will be measured.",
                    "A": "Achievable: Why this goal is achievable.",
                    "R": "Relevant: How this goal is relevant to the 5-year plan.",
                    "T": "Time-bound: The specific deadline for this goal."
                  }
                }
              ]
            }
          ]
        }

        Rules:
        - Hyper-Personalization Mandate: Every quarterly goal for Year 1 must begin by referencing a specific detail from the user's resume. No exceptions. A generic goal like "Obtain a certification" is unacceptable. It must be "Leveraging your `CompTIA Security+`, you will now pursue the `CompTIA CySA+` to build on your security foundation."
        - Location-Awareness: Integrate the user's location (`Tucson, AZ`) where relevant, such as suggesting specific local networking events, companies, or regional industry trends.
        - No Generic Verbs: Avoid vague verbs like "learn," "improve," or "work on." Use concrete action verbs like "implement," "deploy," "master," "achieve," "attain," or "lead."
        - JSON only, no markdown or prose.
        - If not enough details are available in the resume, avoid overcompensating and play it safe; do the best you can with what you have but don’t squeeze juice out of it if it’s not there.
    """).strip())

    prompt = "\n\n".join(chunks)
    logging.info("Prompt built successfully.")
    return prompt
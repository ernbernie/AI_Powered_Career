# backend/perplexity_prompt_builder.py
import textwrap
import logging
import json

# This function is a placeholder. In a real app, you'd have more robust resume parsing.
def _convert_resume_to_json(resume_text: str) -> str:
    """A simple fallback for converting resume text to a JSON object."""
    logging.info("Converting resume snippet to JSON for Perplexity prompt.")
    # For now, we'll just wrap the text in a simple JSON structure.
    return json.dumps({"resume_summary": resume_text}, indent=2)

def build_perplexity_prompt(roadmap_json: str, resume_snippet: str, location: str) -> str:
    """
    Builds a hyper-specific, structured prompt for Perplexity to generate a 
    market intelligence report.
    """
    logging.info("Building hyper-personalized Perplexity prompt...")
    
    resume_json_str = _convert_resume_to_json(resume_snippet)
    
    # This is the prompt structure from your CLI version.
    header = textwrap.dedent(f"""
        You are **MarketIntelPro**, an expert market-intelligence assistant. Your analysis must be forensic, data-driven, and directly tied to the user's provided information. You will produce a deep, action-oriented report that maps every insight back to the user's 5-year career roadmap and resume.

        **Location:** {location}

        **User Resume (JSON):**
        ```json
        {resume_json_str}
        ```

        **5-Year Roadmap (JSON):**
        ```json
        {roadmap_json}
        ```

        **Sources to Prioritize:** 1) LinkedIn  
        2) Tech News & Company Blogs  
        3) Local Event Aggregators (e.g., Meetup.com) in the user's location
        4) Reddit (for anecdotal signals)
    """).strip()

    # --- REFINED INSTRUCTIONS ---
    # These instructions are more forceful and provide a clear formula for the AI.
    tasks = textwrap.dedent("""
        ### Core Task & Analysis Formula

        Your task is to generate a market intelligence report by executing the following formula. You must find real, verifiable data from your online sources.

        **1. Executive Summary:**
           - Write a 2-3 sentence summary of the key market opportunities that align with the user's overall 5-year goal.

        **2. Per-Year Analysis (Repeat for Each of the 5 Years):**
           - **Restate the Goal:** Begin with a markdown header: `## Analysis for Year X: "{The user's goal for that year}"`
           - **Market Signal Validation:** Find one specific, current market trend or technology demand that validates this yearly goal. State the trend and cite your source with a URL.
           - **Actionable Intelligence (2 Items Required):** Provide exactly two distinct, actionable items that directly support this goal. For each item, you must include a justification.
             - **Item 1:** [Name of Event/Company/Course] - [Link]
               - **Justification:** Explain *why* this is a perfect fit by referencing a specific detail from the user's resume. (e.g., "Based on your resume's mention of `PowerShell`, this `Azure DevOps` workshop is a logical next step...")
             - **Item 2:** [Name of Event/Company/Course] - [Link]
               - **Justification:** Explain *why* this is a perfect fit by referencing a different detail from the user's resume.

        **3. Final Checklist:**
           - Conclude with a "Next Steps" checklist. You must use the user's exact Q1-Q4 goal language from the roadmap JSON.
    """).strip()

    # The output structure provides a clear template for the AI to follow.
    output_structure = textwrap.dedent("""
        ### Expected Report Structure (Use this Markdown format exactly)

        # Market Intelligence Report

        ## Executive Summary
        ...

        ---

        ## Analysis for Year 5: "{Year 5 Goal Text}"
        - **Market Signal:** ... [*Source URL*]
        - **Actionable Intelligence:**
            1.  **[Event/Company/Course Name]:** ... [*Link to item*]
                - **Justification:** Based on your resume's mention of `...`, this is relevant because ...
            2.  **[Event/Company/Course Name]:** ... [*Link to item*]
                - **Justification:** Your experience with `...` makes this an ideal opportunity to ...

        (Repeat the analysis structure for Years 4, 3, 2, and 1)

        ---

        ### Next Steps
        - [ ] **Q1:** {user's Q1 goal text}
        - [ ] **Q2:** {user's Q2 goal text}
        - [ ] **Q3:** {user's Q3 goal text}
        - [ ] **Q4:** {user's Q4 goal text}
    """).strip()

    prompt = "\n\n".join([header, tasks, output_structure])
    logging.info(f"Built hyper-personalized Perplexity prompt ({len(prompt)} chars)")
    return prompt

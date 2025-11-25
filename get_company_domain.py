import google.generativeai as genai

def get_company_domain(company_name, gemini_api_key):
    """
    Uses Gemini Grounded Search to fetch company domain.
    """
    gemini_api_key = "AIzaSyBWl-SujsJPIbCUc82QCT58QVykHgNsijU"
    genai.configure(api_key=gemini_api_key)

    prompt = f"""
    Find the official website domain of the company: "{company_name}".
    Respond ONLY with the domain, nothing else.
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # cheap + fast
        response = model.generate_content(prompt)
        domain = response.text.strip()

        # Clean unexpected output
        domain = domain.replace("http://", "").replace("https://", "").strip("/")
        return domain

    except Exception as e:
        print(f"Error finding domain for {company_name}: {e}")
        return None

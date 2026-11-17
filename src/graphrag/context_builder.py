
def build_context(graph_results):
    """
    Convert graph retrieval results into structured text context
    for the LLM.
    """

    if not graph_results:
        return "No relevant company information was found."

    context_parts = []

    for company in graph_results:
        company_context = []

        company_context.append(
            f"Company: {company.get('company', 'Unknown')}"
        )
        company_context.append(
            f"Sector: {company.get('sector', 'Unknown')}"
        )
        company_context.append(
            f"Description: {company.get('description', 'Not available')}"
        )

        # Founders
        founders = company.get("founders", [])
        if founders:
            company_context.append("\nFounders:")
            for founder in founders:
                if founder.get("name"):
                    company_context.append(
                        f"- {founder['name']}, "
                        f"Role: {founder.get('role', 'Unknown')}, "
                        f"Founded in: {founder.get('founded_year', 'Unknown')}"
                    )

        # Investors
        investors = company.get("investors", [])
        if investors:
            company_context.append("\nInvestors:")
            for investor in investors:
                if investor.get("name"):
                    company_context.append(
                        f"- {investor['name']}, "
                        f"Round: {investor.get('round', 'Unknown')}, "
                        f"Amount: {investor.get('amount_million', 'Unknown')} million USD, "
                        f"Year: {investor.get('year', 'Unknown')}"
                    )

        # Products
        products = company.get("products", [])
        if products:
            company_context.append("\nProducts:")
            for product in products:
                if product:
                    company_context.append(f"- {product}")

        # Company Awards
        awards = company.get("awards", [])
        if awards:
            company_context.append("\nCompany Awards:")
            for award in awards:
                if award:
                    company_context.append(f"- {award}")

        # Acquisitions
        acquisitions = company.get("acquisitions", [])
        if acquisitions:
            company_context.append("\nAcquisitions:")
            for acquisition in acquisitions:
                if acquisition.get("name"):
                    company_context.append(
                        f"- {acquisition['name']}, "
                        f"Year: {acquisition.get('year', 'Unknown')}, "
                        f"Amount: {acquisition.get('amount_million', 'Unknown')} million USD"
                    )

        # Founder Awards
        founder_awards = company.get("founder_awards", [])
        if founder_awards:
            company_context.append("\nFounder Awards:")
            for award in founder_awards:
                if award:
                    company_context.append(f"- {award}")

        context_parts.append("\n".join(company_context))

    return "\n\n" + ("\n\n" + "=" * 50 + "\n\n").join(context_parts)


from src.graphrag.generation import LLMGeneration


def main():
    llm = LLMGeneration()

    context = """
    Company: NovaPay
    Sector: Fintech
    Description: A digital payments platform enabling instant cross-border transfers.

    Founders:
    - Elena Rossi, Role: CEO, Founded in: 2016

    Investors:
    - Summit Ventures, Round: Series A, Amount: 15 million USD, Year: 2017
    - Summit Ventures, Round: Series B, Amount: 45 million USD, Year: 2019
    - Northstar Capital, Round: Series C, Amount: 120 million USD, Year: 2021

    Products:
    - NovaPay Wallet
    - NovaPay Business

    Acquisitions:
    - FoodChain, Year: 2023, Amount: 260 million USD
    """

    question = "Who founded NovaPay and how much investment did it receive?"

    print("\nQuestion:")
    print(question)

    answer = llm.generate_answer(
        question=question,
        context=context
    )

    print("\n========== LLM ANSWER ==========")
    print(answer)

    print("\nLLM Generation completed!")


if __name__ == "__main__":
    main()

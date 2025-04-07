import streamlit as st
import yfinance as yf
import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
import matplotlib.pyplot as plt

def risk_questionnaire():
    """Asks the client a questionnaire to gauge risk tolerance and timeline."""
    st.header("Risk Questionnaire")
    questions = [
        ("What is your age?", ['18-25', '26-33', '34-42', '43-50', '50+']),
        ("What is your investment timeline (in years)?", ['1-5', '5-10', '10-20', '20-30', '30+']),
        ("How comfortable are you with market volatility?", ["Very Uncomfortable", "Uncomfortable", "Neutral", "Comfortable", "Very Comfortable"]),
        ("What is your primary investment goal?", ["Preservation of capital", "Income generation", "Growth", "Speculation"]),
        ("How much of your income are you willing to invest?", ["<10%", "10-20%", "20-30%", "30-50%", ">50%"]),
        ("How would you react to a 20% drop in your portfolio?", ["Sell everything", "Sell some", "Hold", "Buy some", "Buy more"]),
        ("What is your current financial situation?", ["Debt-heavy", "Stable", "Comfortable", "Wealthy"]),
        ("How much investment experience do you have?", ["None", "Little", "Some", "Experienced"]),
        ("What is your risk tolerance?", ["Very Conservative", "Conservative", "Moderate", "Aggressive", "Very Aggressive"]),
        ("What is your current net worth?", ["<10,000", "10,000-50,000", "50,000-200,000", "200,000-1,000,000", ">1,000,000"])
    ]

    answers = []
    for question, options in questions:
        choice = st.radio(question, options)
        answers.append(choice)

    return answers

def calculate_risk_score(answers):
    """Calculates a risk score based on questionnaire answers."""
    scores = {
        "What is your age?": {'18-25': 5, '26-33': 4, '34-42': 3, '43-50': 2, '50+':1},
        "What is your investment timeline (in years)?": {'1-5': 1, '5-10': 2, '10-20': 3, '20-30': 4, '30+': 5},
        "How comfortable are you with market volatility?": {"Very Uncomfortable": 1, "Uncomfortable": 2, "Neutral": 3, "Comfortable": 4, "Very Comfortable": 5},
        "What is your primary investment goal?": {"Preservation of capital": 1, "Income generation": 2, "Growth": 4, "Speculation": 5},
        "How much of your income are you willing to invest?": {"<10%": 1, "10-20%": 2, "20-30%": 3, "30-50%": 4, ">50%": 5},
        "How would you react to a 20% drop in your portfolio?": {"Sell everything": 1, "Sell some": 2, "Hold": 3, "Buy some": 4, "Buy more": 5},
        "What is your current financial situation?": {"Debt-heavy": 1, "Stable": 3, "Comfortable": 4, "Wealthy": 5},
        "How much investment experience do you have?": {"None": 1, "Little": 2, "Some": 3, "Experienced": 4},
        "What is your risk tolerance?": {"Very Conservative": 1, "Conservative": 2, "Moderate": 3, "Aggressive": 4, "Very Aggressive": 5},
        "What is your current net worth?": {"<10,000": 1, "10,000-50,000": 2, "50,000-200,000": 3, "200,000-1,000,000": 4, ">1,000,000": 5}
    }

    total_score = 0
    for i, question in enumerate(scores):
        total_score += scores[question][answers[i]]

    return total_score / len(answers)

def get_portfolio(risk_score):
    """Generates a portfolio based on the risk score."""
    tickers = ["VOO",'QQQ', 'AGG', 'VEA', 'XLF','XLK','XLE', 'XLV', 'AGG', 'TLT', 'HYG', 'IWM', 'SCHD'] #Example tickers
    data = yf.download(tickers, period="5y", auto_adjust=False)["Adj Close"]

    mu = expected_returns.mean_historical_return(data)
    S = risk_models.sample_cov(data)

    ef = EfficientFrontier(mu, S, weight_bounds=(0, 0.25)) #Max weight 25%
    if risk_score < 2:
        weights = ef.efficient_return(target_return=0.05) # 5% target return
    elif risk_score < 3:
        weights = ef.efficient_return(target_return=0.08) # 8% target return
    elif risk_score < 4:
        weights = ef.efficient_return(target_return=0.11) # 11% target return
    else:
        weights = ef.max_sharpe()

    cleaned_weights = ef.clean_weights()

    return cleaned_weights

def display_portfolio(weights, tickers):
    """Displays the portfolio in a dashboard."""
    st.header("Your Portfolio")
    st.write(f"Your risk score is {risk_score} out of 5")

    st.write("Here is your personalized portfolio based on your risk profile:")

    # Filter out tickers with 0% weights before printing and visualization
    filtered_weights = {ticker: weight for ticker, weight in weights.items() if weight > 0}

    for ticker, weight in filtered_weights.items():  # Iterate through filtered_weights
        st.write(f"{ticker}: {weight * 100:.2f}%")

    #Visualization
    labels = list(filtered_weights.keys())
    values = list(filtered_weights.values())

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title("Portfolio Allocation")
    st.pyplot(fig)


#"Main function to run the portfolio advisor."

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ("Home", "Questionnaire", "Portfolio"))

if page == "Home":
    st.title("Home Page")
    st.write("Welcome to the portfolio robot advisor!")
    st.write("Use the sidebar to navigate to different sections.")

elif page == "Questionnaire":
    st.title("Risk Assessment Questionnaire")
    # Your questionnaire code here (as in the previous examples)
    st.write("This is where the questionnaire will go.")

    answers = risk_questionnaire()
    st.session_state.answers = answers


elif page == "Portfolio":
    st.title("Portfolio Recommendation")
    # Your portfolio generation and display code here
    st.write("This is where the portfolio will be displayed.")
    if "answers" in st.session_state:
        risk_score = calculate_risk_score(st.session_state.answers)
    else:
        st.error("Please complete the questionnaire first.")
        st.stop()
    risk_score = calculate_risk_score(st.session_state.answers)
    weights = get_portfolio(risk_score)

    display_portfolio(weights, weights.keys())

import { createContext, useState } from "react";
import run from "../config/gemini";

export let Context = createContext();

const ContextProvider = (props) => {
  let [input, setInput] = useState("");
  let [recentPrompt, setRecentPrompt] = useState("");
  let [showResult, setShowResult] = useState(false);
  let [loading, setLoading] = useState(false);
  let [resultData, setResultData] = useState("");
  let [finalresultData, setFinalResultData] = useState("");

  // code analysis

  let [inputAnalysis, setInputAnalysis] = useState("");
  let [recentPromptAnalysis, setRecentPromptAnalysis] = useState("");
  let [showResultAnalysis, setShowResultAnalysis] = useState(false);
  let [loadingAnalysis, setLoadingAnalysis] = useState(false);
  let [resultDataAnalysis, setResultDataAnalysis] = useState("");

  let delayPara = (index, nextWord) => {
    setTimeout(function () {
      setResultData((prev) => prev + nextWord);
    }, 75 * index);
    
  };

  // code analysis

  let delayParaAnalysis = (index, nextWord) => {
    setTimeout(function () {
      setResultDataAnalysis((prev) => prev + nextWord);
    }, 75 * index);
  };

  let onSent = async (prompt) => {
    setResultData("");
    setFinalResultData("");
    setRecentPrompt("");
    setLoading(true);
    setShowResult(true);
    try {
      const response = await run(prompt);
      setFinalResultData(response);
      const responseWords = response.split(" ");
      for (let i = 0; i < responseWords.length; i++) {
        delayPara(i, responseWords[i] + " ");
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Code analysis failed.";
      setFinalResultData(message);
      setResultData(message);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

  // code analysis

  let onSentAnalysis = async (prompt) => {
    setResultDataAnalysis("");
    setLoadingAnalysis(true);
    setShowResultAnalysis(true);
    try {
      const response = await run(prompt);
      const responseArray = response.split("**");
      let formattedResponse = "";
      for (let i = 0; i < responseArray.length; i++) {
        if (i === 0 || i % 2 !== 1) {
          formattedResponse += responseArray[i];
        } else {
          formattedResponse += "<b>" + responseArray[i] + "</b>";
        }
      }
      const formattedWords = formattedResponse.split("*").join("</br>").split(" ");
      for (let i = 0; i < formattedWords.length; i++) {
        delayParaAnalysis(i, formattedWords[i] + " ");
      }
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Code analysis failed.";
      setResultDataAnalysis(message);
    } finally {
      setLoadingAnalysis(false);
      setInputAnalysis("");
    }
  };

  let contextValue = {
    input,
    setInput,
    recentPrompt,
    setRecentPrompt,
    showResult,
    onSent,
    setShowResult,
    resultData,
    setResultData,
    loading,
    setLoading,
    finalresultData,
    setFinalResultData,
    // code analysis

    inputAnalysis,
    setInputAnalysis,
    recentPromptAnalysis,
    setRecentPromptAnalysis,
    showResultAnalysis,
    onSentAnalysis,
    setShowResultAnalysis,
    resultDataAnalysis,
    setResultDataAnalysis,
    loadingAnalysis,
    setLoadingAnalysis,
  };

  return (
    <Context.Provider value={contextValue}>{props.children}</Context.Provider>
  );
};

export default ContextProvider;

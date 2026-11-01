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

  let onSent = async (prompt) => {
    setResultData("");
    setFinalResultData("");
    setRecentPrompt("");
    setLoading(true);
    setShowResult(true);
    try {
      const response = await run(prompt);
      setFinalResultData(response);
      setResultData(response);
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Code analysis failed.";
      setFinalResultData("");
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
      setResultDataAnalysis(response);
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

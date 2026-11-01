import * as React from "react";
import PropTypes from "prop-types";

import CssBaseline from "@mui/material/CssBaseline";
import Box from "@mui/material/Box";
import Editor from "@monaco-editor/react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import Stack from "@mui/material/Stack";
import Typography from "@mui/material/Typography";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";
import Container from "@mui/material/Container";
import DebugResponse from "./DebugResponse";
import AppAppBar from "./AppAppBar";
import Footer from "./Footer";
import getLPTheme from "../getLPTheme";
import { Button, Divider } from "@mui/material";
import { useRef } from "react";
import { Context } from "../../context/context";
import { IoChatbubbleEllipses } from "react-icons/io5";
import { getToken } from "../../services/localStorageService";
import { useReportDataQuery } from "../../services/userAuthApi";

function ToggleCustomTheme({ showCustomTheme, toggleCustomTheme }) {
  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        width: "100dvw",
        position: "fixed",
        bottom: 24,
      }}
    >
      <ToggleButtonGroup
        color="primary"
        exclusive
        value={showCustomTheme}
        onChange={toggleCustomTheme}
        aria-label="Platform"
        sx={{
          backgroundColor: "background.default",
          "& .Mui-selected": {
            pointerEvents: "none",
          },
        }}
      ></ToggleButtonGroup>
    </Box>
  );
}

ToggleCustomTheme.propTypes = {
  showCustomTheme: PropTypes.bool.isRequired,
  toggleCustomTheme: PropTypes.func.isRequired,
};

export default function UserChat() {
  const [mode, setMode] = React.useState("dark");
  const [showCustomTheme, setShowCustomTheme] = React.useState(true);
  const LPtheme = createTheme(getLPTheme(mode));
  const defaultTheme = createTheme({ palette: { mode } });

  const { access_token } = getToken();

  const {
    data,
    isLoading,
    isError,
    error,
  } = useReportDataQuery(access_token, { skip: !access_token });
  const reportData = data?.data ?? [];
  const [selectedReport, setSelectedReport] = React.useState(null);
  const initialReport = {
    bug_code: "Click Report Title To Show Data Here...",
    bug_report: "Click Report Title To Show Data Here...",
  };
  const reportError =
    error?.data?.detail || error?.error || "Could not load reports.";

  const toggleColorMode = () => {
    setMode((prev) => (prev === "dark" ? "dark" : "dark"));
  };

  const toggleCustomTheme = () => {
    setShowCustomTheme((prev) => !prev);
  };

  let editorRef = useRef(null);

  function handleEditorDidMount(editor, monaco) {
    editorRef.current = editor;
  }

  return (
    <ThemeProvider theme={showCustomTheme ? LPtheme : defaultTheme}>
      <CssBaseline />
      <AppAppBar mode={mode} toggleColorMode={toggleColorMode} />

      <Box sx={{ bgcolor: "background.default" }}>
        <div
          style={{
            marginTop: "18vh",
            display: "flex",
            flexDirection: "column",
            gap: 10,
          }}
        >
          <Typography
            component="h1"
            variant="h1"
            sx={{
              display: "flex",
              flexDirection: { xs: "column", md: "row" },
              alignSelf: "center",
              textAlign: "center",
            }}
          >
            Yours Recents&nbsp;
            <Typography
              component="span"
              variant="h1"
              sx={{
                color: (theme) =>
                  theme.palette.mode === "light"
                    ? "primary.main"
                    : "primary.light",
              }}
            >
              Reports
            </Typography>
          </Typography>
          <Typography variant="body1" textAlign="center" color="text.secondary">
            Our website provide collection of your reports, designed specifically
            for programmers where you can preview your reports at anytime. <br />
          </Typography>
        </div>

        <Divider
          sx={{
            marginTop: "10vh",
            backgroundColor: "#7069cc",
          }}
        ></Divider>

        <div
          style={{
            // backgroundColor:"#fff",
            width: "99%",
            height: "90vh",
            // marginTop:"15vh",
            display: "flex",
            // marginLeft:"1vw",
            // marginRight:"1vw"
          }}
        >
          <div
            style={{
              backgroundColor: "#181a29",
              width: "19%",
              height: "90vh",
              overflow: "overlay",
              scrollbarWidth: "thin",
            }}
          >
            <div
              style={{
                textAlign: "center",
                marginTop: 10,
              }}
            >
              <p
                style={{
                  fontSize: 20,
                  fontWeight: "bold",
                  letterSpacing: 1,
                }}
              >
                Reports Title
              </p>
              <Divider></Divider>

              <div
                style={{
                  marginTop: 15,
                  marginBottom: 15,
                }}
              >
                {/* chat title */}
                {isLoading ? (
                  <p>Loading reports...</p>
                ) : isError ? (
                  <p role="alert">{String(reportError)}</p>
                ) : reportData.length > 0 ? (
                  reportData.map((item, index) => (
                    <button
                      key={`${item.title}-${index}`}
                      type="button"
                      onClick={() => setSelectedReport(item)}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "center",
                        gap: 8,
                        margin: "18px auto",
                        padding: "6px 10px",
                        border: 0,
                        background: "transparent",
                        color: "inherit",
                        cursor: "pointer",
                        letterSpacing: 1,
                      }}
                    >
                      <IoChatbubbleEllipses style={{ fontSize: "20px" }} />
                      <span>{item.title.slice(0, 24)}</span>
                    </button>
                  ))
                ) : (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <div
                      style={{
                        marginTop: 5,
                      }}
                    >
                      <IoChatbubbleEllipses
                        style={{
                          fontSize: "20px",
                        }}
                      />
                    </div>
                    <div
                      style={{
                        marginLeft: 8,
                      }}
                    >
                      <p
                        style={{
                          fontSize: 15,
                          letterSpacing: 1,
                        }}
                      >
                        No reports yet. Run or analyze code, then save a report.
                      </p>
                    </div>
                  </div>
                )}
              </div>

              <Divider></Divider>
            </div>
          </div>

          {/* body div */}
          <div
            style={{
              // backgroundColor:"#fcba03",
              width: "80%",
              height: "100vh",
            }}
          >
            <div
              style={{
                display: "flex",
                marginTop: "1rem",
                marginBottom: "5rem",
              }}
            >
              <div
                class="editor-container"
                style={{
                  width: "36%",
                  height: "540px",
                  marginLeft: 25,
                  position: "relative",
                  marginBottom: 150,
                }}
              >
                <div
                  style={
                    {
                      // marginTop: "5rem",
                    }
                  }
                >
                  <p
                    style={{
                      color: "#fff",
                      letterSpacing: 1,
                    }}
                  >
                    Your Code :
                  </p>
                </div>
                <Box
                  height="72vh"
                  width="38vw"
                  p={2}
                  overflow="overlay"
                  border="3px solid"
                  borderRadius={4}
                  borderColor="#0959AA"
                  marginTop="25px"
                >
                  <Typography
                    component="pre"
                    sx={{
                      fontSize: "17px",
                      fontWeight: 300,
                      lineHeight: 1.8,
                      whiteSpace: "pre-wrap",
                      overflowWrap: "anywhere",
                      fontFamily: "inherit",
                    }}
                  >
                    {selectedReport?.bug_code ?? initialReport.bug_code}
                  </Typography>
                </Box>
              </div>
              <div
                style={{
                  marginLeft: "11vw",
                }}
              >
                <div
                  style={{
                    marginBottom: "1.5rem",
                    // marginTop: "2rem",
                  }}
                >
                  <p
                    style={{
                      color: "#fff",
                      letterSpacing: 1,
                    }}
                  >
                    Report Response :
                  </p>
                </div>
                {/* runner component */}
                <Box
                  height="72vh"
                  width="38vw"
                  p={2}
                  overflow="overlay"
                  border="3px solid"
                  borderRadius={4}
                  borderColor="#0959AA"
                >
                  <Typography
                    component="pre"
                    sx={{
                      fontSize: "17px",
                      fontWeight: 300,
                      lineHeight: 1.8,
                      whiteSpace: "pre-wrap",
                      overflowWrap: "anywhere",
                      fontFamily: "inherit",
                    }}
                  >
                    {selectedReport?.bug_report ?? initialReport.bug_report}
                  </Typography>
                </Box>
              </div>
            </div>
          </div>
        </div>

        {/* {!showResult ? <></> : <DebugResponse></DebugResponse>} */}
        <Divider sx={{ backgroundColor: "#7069cc" }} />
        <Footer />
      </Box>
      <ToggleCustomTheme
        showCustomTheme={showCustomTheme}
        toggleCustomTheme={toggleCustomTheme}
      />
    </ThemeProvider>
  );
}

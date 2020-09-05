import React, { useEffect, useState } from "react";
import AceEditor from "react-ace";

import "ace-builds/src-noconflict/mode-java";
import "ace-builds/src-noconflict/theme-github";
import { getCode } from "../util/http";
import { useDebounce } from "use-debounce";

import "./Home.css";
import KeywordBubble from "./KeywordBubble";

const KEYWORDS = ["graph", "named", "called", "has"];

const TYPES = ["float", "string", "bool", "datetime", "int", "double"];
const SUPPORTED_GSQL = [
  "Vertices",
  "Directed edges",
  "Undirected edges",
  "Vertex properties",
  "Edge properties",
  "Graph",
];

const SAMPLE_TEXT =
  "I have a graph called Bankworld. A person has an account at a bank. A bank has an name and location. An account has a float balance.";

function Home() {
  const [text, setText] = useState(SAMPLE_TEXT || "");

  const [debounceText] = useDebounce(text, 1000);
  const [result, setResult] = useState("");

  useEffect(() => {
    console.log("debounce text", debounceText);
    if (debounceText) {
      getCode(debounceText).then((result) => {
        const data = result.data;
        console.log("data", data);
        setResult(data);
      });
    }
  }, [debounceText]);

  return (
    <div className="main-area">
      <div className="subheader">
        Create GSQL instantly from English sentences.
      </div>
      <div style={{ height: "50px" }} />
      <div className="columns">
        <div className="column is-half">
          <div className="header-text">
            Enter your description on the left...
          </div>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            className="textarea"
            placeholder="I want a graph called..."
            rows="10"
          />
          <h2 className="header-text">Keywords</h2>
          {KEYWORDS.map((word, i) => (
            <KeywordBubble
              key={i}
              word={word}
              onClick={(w) => setText(text + " " + w)}
            />
          ))}
          <h2 className="header-text">Types</h2>
          {TYPES.map((word, i) => (
            <KeywordBubble
              key={i}
              word={word}
              onClick={(w) => setText(text + " " + w)}
            />
          ))}
        </div>
        <div className="column is-half">
          <div className="header-text">See the GSQL on the right...</div>
          <AceEditor
            width={"900px"}
            mode="javascript"
            theme="github"
            fontSize={14}
            value={result && result.code}
            onChange={(e) => setResult({ ...result, code: e })}
            name="UNIQUE_ID_OF_DIV"
            editorProps={{ $blockScrolling: true }}
          />
        </div>
      </div>
      {/* <div className="breakdown-section">{JSON.stringify(codeGraph)}</div> */}
      <h2 className="header-text">Limitations</h2>
      <div className="upload-section">
        <p>
          Use simple sentences. Sentences are expected to have one subject and
          possible multiple direct objects or actions.
        </p>
        <p>Supports the following constructs:</p>
        {SUPPORTED_GSQL.map((v, i) => {
          return <li key={i}>{v}</li>;
        })}
      </div>
      {result.reasons && result.reasons.length > 0 && (
        <div className="why-section">
          <div className="header-text">Why this result?</div>
          <div>
            {result.reasons.map((r, i) => {
              return <li key={i}>{r}</li>;
            })}
          </div>
        </div>
      )}
    </div>
  );
}
export default Home;

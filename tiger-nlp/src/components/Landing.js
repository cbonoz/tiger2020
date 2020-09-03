import React, { Component } from "react";
import logo from "../assets/tiger_nlp_trans.png";
import tree from "../assets/tree.png";

export default class Landing extends Component {
  render() {
    return (
      <div>
        <div className="header-middle">
          <div className="top-header">
            {/* <Carousel /> */}
            <img src={logo} className="center-logo" />

            <p className="subheader">
              Learn and write&nbsp;
              <a href="https://www.tigergraph.com/gsql" target="_blank">
                GSQL
              </a>
              &nbsp;for Tigergraph
              <br />
              using English sentences.
            </p>
            <a href="/start">
              <button className="button is-primary">Get Started</button>
            </a>
          </div>
          <div className="faq-section">
            <div className="subheader">What is TigerNLP?</div>
            <p>
              TigerNLP is a web app allowing you to generate GSQL scaffolding
              code from written sentences. Use TigerNLP to bootstrap your next
              Tigergraph project and learn about graph networks. Powered by a
              spaCy NLP server.
            </p>
          </div>
          <img src={tree} className="tree-image" />
        </div>
      </div>
    );
  }
}

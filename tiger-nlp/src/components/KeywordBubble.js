import React, { Component } from 'react';

export default function KeywordBubble(props) {
	const { word, onClick } = props;

	return (
		<div
			className="keyword-bubble"
			onClick={() => {
				onClick(word);
			}}
		>
			{word}
		</div>
	);
}

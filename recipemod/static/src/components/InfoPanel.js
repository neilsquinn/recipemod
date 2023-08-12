import React from "react";

function InfoPanel(props) {
  const info = props.info;
  return (
    <ul className="list-group list-group-horizontal small">
      {info.map(({ label, value }) => {
        return (
          <li key={label} className="list-group-item">
            <span className="font-weight-bold">{label}: </span>
            <span className="font-italic">{value}</span>
          </li>
        );
      })}
    </ul>
  );
}

export default InfoPanel;

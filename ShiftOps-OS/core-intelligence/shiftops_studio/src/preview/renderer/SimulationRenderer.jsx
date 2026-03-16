import React from 'react';
import { Box, Line, Circle, Label } from "./primitives"

export default function SimulationRenderer({ model }) {

  if (!model) return null

  return (
    <svg width="800" height="500" viewBox="0 0 800 500" style={{ maxWidth: '100%', height: 'auto' }}>

      {model.elements.map((el, i) => {

        switch(el.type) {

          case "box":
            return <Box key={i} {...el} />

          case "line":
            return <Line key={i} {...el} />

          case "circle":
            return <Circle key={i} {...el} />

          case "text":
            return <Label key={i} x={el.x} y={el.y} text={el.label} />

          default:
            return null

        }

      })}

    </svg>
  )
}

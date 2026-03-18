export function Box({x,y,w,h}) {
  return (
    <rect
      x={x}
      y={y}
      width={w}
      height={h}
      stroke="#60a5fa"
      fill="none"
      strokeWidth="2"
    />
  )
}

export function Line({x1,y1,x2,y2}) {
  return (
    <line
      x1={x1}
      y1={y1}
      x2={x2}
      y2={y2}
      stroke="#93c5fd"
      strokeWidth="2"
    />
  )
}

export function Circle({x,y,r}) {
  return (
    <circle
      cx={x}
      cy={y}
      r={r}
      stroke="#93c5fd"
      fill="none"
      strokeWidth="2"
    />
  )
}

export function Label({x,y,text}) {
  return (
    <text
      x={x}
      y={y}
      fill="#e0f2fe"
      fontSize="14"
      fontFamily="sans-serif"
    >
      {text}
    </text>
  )
}

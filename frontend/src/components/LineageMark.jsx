export default function LineageMark({ size = 28, spinning = false }) {
  return (
    <svg
      className={`lineage-mark${spinning ? " spinning" : ""}`}
      width={size}
      height={size}
      viewBox="0 0 32 32"
      fill="none"
      aria-hidden="true"
    >
      <circle cx="16" cy="6" r="3" fill="currentColor" />
      <circle cx="7" cy="26" r="3" fill="currentColor" />
      <circle cx="25" cy="26" r="3" fill="currentColor" />
      <path
        d="M16 9 L16 16 L7 23 M16 16 L25 23"
        stroke="currentColor"
        strokeWidth="1.5"
        fill="none"
      />
    </svg>
  );
}

export function getUncertaintyLevel(score) {
  if (score === null || score === undefined) {
    return "INSUFFICIENT";
  }

  if (score <= 20) {
    return "LOW";
  }

  if (score <= 40) {
    return "MEDIUM";
  }

  return "HIGH";
}
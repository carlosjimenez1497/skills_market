type Track = "software" | "finance";

interface HomeProps {
  onSelectTrack: (track: Track) => void;
}

export default function Home({ onSelectTrack }: HomeProps) {
  return (
    <div style={{ display: "grid", gap: 12, gridTemplateColumns: "1fr 1fr", marginTop: 16 }}>
      <button
        style={{ padding: 18, borderRadius: 12, border: "1px solid #ddd", textAlign: "left" }}
        onClick={() => onSelectTrack("software")}
      >
        <div style={{ fontSize: 18, fontWeight: 700 }}>Software</div>
        <div style={{ opacity: 0.7 }}>Backend, C++, SDET, data…</div>
      </button>

      <button
        style={{ padding: 18, borderRadius: 12, border: "1px solid #ddd", textAlign: "left" }}
        onClick={() => onSelectTrack("finance")}
      >
        <div style={{ fontSize: 18, fontWeight: 700 }}>Finance</div>
        <div style={{ opacity: 0.7 }}>Quant, analyst, modeling…</div>
      </button>
    </div>
  );
}
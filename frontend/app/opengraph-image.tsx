import { ImageResponse } from "next/og";

export const alt = "production-rag — RAG that shows its work";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

export default function OpengraphImage() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "#FAFAF7",
          padding: "72px 80px",
        }}
      >
        {/* left — headline block */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            width: 640,
            height: "100%",
            justifyContent: "space-between",
          }}
        >
          <div
            style={{
              display: "flex",
              fontSize: 24,
              letterSpacing: 6,
              color: "#1D4ED8",
              textTransform: "uppercase",
            }}
          >
            production-rag · open-source rag infrastructure
          </div>

          <div style={{ display: "flex", flexDirection: "column" }}>
            <div
              style={{
                display: "flex",
                fontSize: 84,
                fontWeight: 700,
                lineHeight: 1.05,
                letterSpacing: -3,
                color: "#14171C",
              }}
            >
              RAG that
            </div>
            <div
              style={{
                display: "flex",
                fontSize: 84,
                fontWeight: 700,
                lineHeight: 1.05,
                letterSpacing: -3,
                color: "#14171C",
              }}
            >
              shows its work.
            </div>
            <div
              style={{
                display: "flex",
                marginTop: 24,
                fontSize: 28,
                lineHeight: 1.4,
                color: "#4E555E",
              }}
            >
              Answers cited to the exact page — or refused when the evidence
              isn&apos;t there.
            </div>
          </div>

          <div style={{ display: "flex", gap: 14 }}>
            {["[n] page-level citations", "refusals over hallucinations", "142 offline tests"].map(
              (chip) => (
                <div
                  key={chip}
                  style={{
                    display: "flex",
                    fontSize: 21,
                    color: "#14171C",
                    border: "1px solid rgba(20,23,28,0.22)",
                    borderRadius: 999,
                    padding: "10px 22px",
                    background: "#FFFFFF",
                  }}
                >
                  {chip}
                </div>
              )
            )}
          </div>
        </div>

        {/* right — terminal trace panel */}
        <div
          style={{
            display: "flex",
            flexDirection: "column",
            width: 400,
            height: "100%",
            background: "#11141A",
            borderRadius: 24,
            padding: "28px 30px",
          }}
        >
          <div style={{ display: "flex", gap: 8, marginBottom: 26 }}>
            {[0, 1, 2].map((i) => (
              <div
                key={i}
                style={{
                  width: 12,
                  height: 12,
                  borderRadius: 999,
                  background: "rgba(255,255,255,0.16)",
                }}
              />
            ))}
          </div>

          <div style={{ display: "flex", fontSize: 21, color: "#D8DCE2", lineHeight: 1.9 }}>
            <span style={{ color: "#8AB0FF", marginRight: 12 }}>$</span>
            retrieve(&quot;vector db search&quot;)
          </div>
          <div style={{ display: "flex", fontSize: 21, color: "#8E96A3", lineHeight: 1.9 }}>
            6 passages · 3 sources · top 0.82
          </div>
          <div style={{ display: "flex", fontSize: 21, color: "#6BC48F", lineHeight: 1.9 }}>
            0.82 above threshold — grounded
          </div>

          <div
            style={{
              display: "flex",
              marginTop: 26,
              background: "rgba(255,255,255,0.04)",
              border: "1px solid rgba(255,255,255,0.09)",
              borderRadius: 14,
              padding: "20px 22px",
              fontSize: 20,
              lineHeight: 1.6,
              color: "#D8DCE2",
            }}
          >
            Qdrant uses the HNSW graph algorithm, trading a small index-time
            cost for fast queries at scale.{" "}
            <span
              style={{
                color: "#8AB0FF",
                border: "1px solid rgba(138,176,255,0.4)",
                background: "rgba(29,78,216,0.18)",
                borderRadius: 6,
                padding: "0 8px",
                marginLeft: 8,
              }}
            >
              1
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", marginTop: 26, gap: 12 }}>
            {[
              ["[1] qdrant-architecture.pdf · p.3", 82],
              ["[2] qdrant-architecture.pdf · p.4", 74],
              ["[3] retrieval-notes.pdf · p.12", 68],
            ].map(([label, pct]) => (
              <div
                key={label as string}
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  background: "rgba(255,255,255,0.03)",
                  border: "1px solid rgba(255,255,255,0.08)",
                  borderRadius: 10,
                  padding: "12px 16px",
                }}
              >
                <span style={{ display: "flex", fontSize: 18, color: "#8E96A3" }}>
                  {label}
                </span>
                <span
                  style={{
                    display: "flex",
                    width: 70,
                    height: 6,
                    borderRadius: 999,
                    background: "rgba(255,255,255,0.1)",
                    overflow: "hidden",
                  }}
                >
                  <span
                    style={{
                      display: "flex",
                      width: `${pct}%`,
                      height: 6,
                      background: "#1D4ED8",
                    }}
                  />
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    ),
    size
  );
}

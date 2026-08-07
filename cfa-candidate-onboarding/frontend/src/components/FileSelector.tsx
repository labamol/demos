import type { MockFile } from "../types";

interface Props {
  files: MockFile[];
  selected: string | null;
  onSelect: (name: string) => void;
}

export default function FileSelector({ files, selected, onSelect }: Props) {
  return (
    <div className="card">
      <h2>Mock candidate files</h2>
      <p className="muted">Local directory storage, listed through the MCP file server.</p>
      {files.map((file) => (
        <div
          key={file.name}
          className={`file-item${selected === file.name ? " selected" : ""}`}
          onClick={() => onSelect(file.name)}
        >
          <strong>{file.candidate_name ?? file.name}</strong>
          <small>{file.persona}</small>
          <br />
          <small className="mono">{file.path}</small>
        </div>
      ))}
      {files.length === 0 && <p className="muted">No profile files found in data/mock/applications.</p>}
    </div>
  );
}

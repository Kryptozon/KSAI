export default function AgentSelect({ agent, setAgent }) {
  const agents = [
    { id: "default", name: "General Assistant" },
    { id: "researcher", name: "Crypto Researcher" },
    { id: "teacher", name: "Tutor" },
    { id: "sales", name: "Sales Bot" },
    { id: "planner", name: "Workflow Planner" },
    { id: "crypto", name: "Crypto Analyst" }
  ];

  return (
    <div className="flex gap-4 p-2 bg-gray-200">
      {agents.map((a) => (
        <button
          key={a.id}
          className={`px-4 py-2 rounded ${
            agent === a.id ? "bg-blue-500 text-white" : "bg-white"
          }`}
          onClick={() => setAgent(a.id)}
        >
          {a.name}
        </button>
      ))}
    </div>
  );
}

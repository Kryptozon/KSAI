export default function UploadBox() {
  const uploadFile = async () => {
    const input = document.getElementById("fileInput");
    if (!input.files.length) return alert("Select a file first!");
    const formData = new FormData();
    formData.append("file", input.files[0]);
    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: formData
    });
    const data = await res.json();
    alert(data.status);
  };

  return (
    <div className="p-2 bg-gray-100">
      <input type="file" id="fileInput" />
      <button
        className="ml-2 px-3 py-1 bg-blue-500 text-white rounded"
        onClick={uploadFile}
      >
        Upload Doc
      </button>
    </div>
  );
}

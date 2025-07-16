import { useState } from "react";
import axios from "axios";

export default function App() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [resume, setResume] = useState(null);
  const [education, setEducation] = useState("");
  const [skills, setSkills] = useState("");
  const [experience, setExperience] = useState("");
  const [results, setResults] = useState([]);
  const [isHR, setIsHR] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);
  const [userType, setUserType] = useState("");

  const handleLogin = (type) => {
    setUserType(type);
    setIsHR(type === "hr");
    setLoggedIn(true);
  };

  const handleLogout = () => {
    setLoggedIn(false);
    setUserType("");
  };

  const handleResumeUpload = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append("name", name);
    formData.append("email", email);
    formData.append("resume", resume);
    
    await axios.post("http://localhost:5000/upload_resume", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    alert("Resume uploaded successfully!");
  };

  const handleMatchResumes = async (e) => {
    e.preventDefault();
    const response = await axios.post("http://localhost:5000/match_resumes", {
      education,
      skills: skills.split(","),
      experience,
    });
    setResults(response.data);
  };

  return (
    <div className="p-5">
      {!loggedIn ? (
        <div>
          <h1 className="text-2xl font-bold">Login</h1>
          <button onClick={() => handleLogin("applicant")} className="bg-blue-500 text-white p-2 m-2">Applicant Login</button>
          <button onClick={() => handleLogin("hr")} className="bg-green-500 text-white p-2 m-2">HR Login</button>
        </div>
      ) : (
        <div>
          <button onClick={handleLogout} className="bg-red-500 text-white p-2">Logout</button>
          {isHR ? (
            <div>
              <h1 className="text-2xl font-bold">HR Portal</h1>
              <form onSubmit={handleMatchResumes} className="mt-6 space-y-3">
                <input type="text" placeholder="Required Education" value={education} onChange={(e) => setEducation(e.target.value)} className="border p-2 w-full" />
                <input type="text" placeholder="Required Skills (comma-separated)" value={skills} onChange={(e) => setSkills(e.target.value)} className="border p-2 w-full" />
                <input type="text" placeholder="Required Experience (years)" value={experience} onChange={(e) => setExperience(e.target.value)} className="border p-2 w-full" />
                <button type="submit" className="bg-green-500 text-white p-2 w-full">Match Resumes</button>
              </form>
              {results.length > 0 && (
                <div className="mt-6">
                  <h2 className="text-xl font-bold">Top Matching Resumes:</h2>
                  <ul className="list-disc ml-5">
                    {results.map(([name, score]) => (
                      <li key={name}>{name}: {score.toFixed(2)}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div>
              <h1 className="text-2xl font-bold">Applicant Portal</h1>
              <form onSubmit={handleResumeUpload} className="mt-4 space-y-3">
                <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} className="border p-2 w-full" />
                <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="border p-2 w-full" />
                <input type="file" onChange={(e) => setResume(e.target.files[0])} className="border p-2 w-full" />
                <button type="submit" className="bg-blue-500 text-white p-2 w-full">Upload Resume</button>
              </form>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

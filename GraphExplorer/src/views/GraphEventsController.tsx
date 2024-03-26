import { useRegisterEvents, useSigma } from "react-sigma-v2";
import React, { FC, useEffect, useState } from "react";

function getMouseLayer() {
  return document.querySelector(".sigma-mouse");
}

function openTeacherProfile(node: any, graph:any) {
  const teacherName = node.label; // Assuming 'label' holds the full name
  const professionalInterests = node.professionalInterests; // Assuming this is the array or object holding the interests

  const profileContent = `
    <!DOCTYPE html>
    <html>
    <head>
      <title>${teacherName}'s Profile</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          margin: 20px;
          padding: 20px;
          border: 1px solid #ccc;
        }
      </style>
    </head>
    <body>
      <h1>${teacherName}</h1>
      <h2>Professional Interests</h2>
      <ul>
        ${Object.keys(professionalInterests).map(interest => <li>${interest}: ${professionalInterests[interest]}</li>).join('')}
      </ul>
    </body>
    </html>
  `;

  const profileWindow = window.open('', '_blank');
  if (profileWindow) {
    profileWindow.document.write(profileContent); // Write the profile content to the new window
    profileWindow.document.close(); // Close the document for writing
  }
}

const GraphEventsController: FC<{ setHoveredNode: (node: string | null) => void }> = ({ setHoveredNode, children }) => {
  const sigma = useSigma();
  const graph = sigma.getGraph();
  const registerEvents = useRegisterEvents();
  const [teacherInterests, setTeacherInterests] = useState<{[key: string]: string}>({});

  useEffect(() => {
    async function fetchTeacherInterests() {
      try {
        // Adjust the path to where your JSON is located
        const response = await fetch(`${process.env.PUBLIC_URL}/data/teacher_interests.json}`);
        const data = await response.json();
        setTeacherInterests(data);
      } catch(error) {
        console.error("Failed to load teacher interests", error);
      }
    }

    fetchTeacherInterests();

    // Your existing events registration code here...
  }, [registerEvents, graph, setHoveredNode]);

  return <>{children}</>;
};

export default GraphEventsController;

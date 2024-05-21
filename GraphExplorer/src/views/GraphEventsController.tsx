import { useRegisterEvents, useSigma } from "react-sigma-v2";
import { FC, useEffect } from "react";

function getMouseLayer() {
  return document.querySelector(".sigma-mouse");
}

const GraphEventsController: FC<{ setHoveredNode: (node: string | null) => void }> = ({ setHoveredNode, children }) => {
  const sigma = useSigma();
  const graph = sigma.getGraph();
  const registerEvents = useRegisterEvents();

  /**
   * Initialize here settings that require to know the graph and/or the sigma
   * instance:
   */
  useEffect(() => {
    registerEvents({
		clickNode({ node }) {
		  const label = graph.getNodeAttribute(node, "label");
		  const interests = graph.getNodeAttribute(node, "interests");

		  if (!graph.getNodeAttribute(node, "hidden") && interests) {
			const newWindow = window.open("", "_blank");

			if (newWindow) {
			  // Define a simple HTML template with inline CSS for styling
			  const htmlContent = `
				<!DOCTYPE html>
				<html lang="en">
				<head>
				<meta charset="UTF-8">
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				<title>${label}</title>
				<style>
				  body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
				  h1 { color: #333; }
				  p { color: #555; }
				</style>
				</head>
				<body>
				<h1>${label}</h1>
				<p><b>Профессиональные интересы:</b> ${interests}</p>
				</body>
				</html>
			  `;

			  newWindow.document.open();
			  newWindow.document.write(htmlContent);
			  newWindow.document.close();
			} else {
			  console.error("Failed to open new window");
			}
		  }
		},
		enterNode({ node }) {
			setHoveredNode(node);
			// TODO: Find a better way to get the DOM mouse layer:
			const mouseLayer = getMouseLayer();
			if (mouseLayer) mouseLayer.classList.add("mouse-pointer");
		},
		leaveNode() {
			setHoveredNode(null);
			// TODO: Find a better way to get the DOM mouse layer:
			const mouseLayer = getMouseLayer();
			if (mouseLayer) mouseLayer.classList.remove("mouse-pointer");
      },
    });
  }, [sigma, graph, registerEvents]);

  return <>{children}</>;
};

export default GraphEventsController;

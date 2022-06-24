import NavDrawer from "./NavDrawer";
import "./Content.css";

export default function Content({ children }) {
	return (
		<main>
			<NavDrawer/>
			<div className="main-content">
				{children}
			</div>
		</main>
	)
}
import NavToggle from "../parts/NavToggle";
import "./Navbar.css";

export default function Navbar() {
	return (
		<nav className="nav-bar">
			<NavToggle/>
			<span>Canvas Helpers</span>
		</nav>
	);
}
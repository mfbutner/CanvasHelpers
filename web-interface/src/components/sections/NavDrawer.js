import useGlobal from "../parts/GlobalData";
import "./NavDrawer.css";

export default function NavDrawer() {
	const global = useGlobal();
	const open = global.data.navOpen;

	return (
		<nav className={`nav-drawer ${open ? "nav-drawer-open" : ""}`}>
			9
		</nav>
	);
}
import useGlobal from "../parts/GlobalData";
import "./NavDrawer.css";
import NavDrawerItem from "../parts/NavDrawerItem";

export default function NavDrawer() {
	const global = useGlobal();
	const open = global.data.navOpen;

	return (
		<nav className={`nav-drawer ${open ? "nav-drawer-open" : ""}`}>
			<div className="nav-drawer-contents">
				<NavDrawerItem>
					Upload
				</NavDrawerItem>
				<NavDrawerItem>
					Download
				</NavDrawerItem>
			</div>
		</nav>
	);
}
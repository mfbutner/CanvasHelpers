import useGlobal from "./GlobalData";
import "./NavToggle.css";

export default function NavToggle() {
	const global = useGlobal();
	const opened = global.data.navOpen;
	const toggle = () => global.update({ navOpen: !opened });
	return (
		<button className="nav-toggle" onClick={toggle}>
			Menu
		</button>
	);
}
import "./NavDrawerItem.css";

export default function NavDrawerItem({ children }) {
	return (
		<div className="nav-drawer-item">
			{children}
		</div>
	);
}
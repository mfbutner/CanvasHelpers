import "./DropdownItem.css";

export default function DropdownItem({ type, text, value, onClick }) {
	const onItemClick = type !== "download" ? onClick : undefined;

	return (
		<div className="dropdown-item" onClick={onItemClick}>
			<div className="dropdown-item-text">
				{text}
			</div>
			{type === "download" && (
				<button className="dropdown-item-download">
					Download
				</button>
			)}
		</div>
	);
}
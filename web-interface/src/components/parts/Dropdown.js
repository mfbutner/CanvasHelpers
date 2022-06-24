import { useState } from "react";
import DropdownItem from "./DropdownItem";
import "./Dropdown.css";

export default function Dropdown({ title, items, type }) {
	const [selected, setSelected] = useState([]);

	const toggleSelect = value => {
		const newSelected = [...selected];
		if(selected.includes(value)) {
			newSelected.splice(newSelected.indexOf(value), 1);
		} else {
			newSelected.push(value);
		}
		setSelected(newSelected);
	}

	return (
		<div className="dropdown-container">
			<div className="dropdown-title">
				{title}
			</div>
			<div className="dropdown-list">
				{
					items.map(item => (
						<DropdownItem
							key={item.value}
							{...item}
							type={type}
							onClick={toggleSelect}
							selected={selected.includes(item.value)}
						/>
					))
				}
			</div>
		</div>
	);
};
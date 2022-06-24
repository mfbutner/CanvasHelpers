import './Home.css';
import Navbar from "../components/sections/Navbar";
import Dropdown from "../components/parts/Dropdown";
import Content from "../components/sections/Content";

function Home() {
	const testData = [
		{
			text: "ECS 36A",
			value: "999"
		},
		{
			text: "ECS 36A",
			value: "99"
		},
		{
			text: "ECS 36A",
			value: "9"
		},
	];

	return (
		<div className="home">
			<Navbar/>
			<Content>
				<Dropdown
					title="Classes"
					items={testData}
					type="download"
				/>
			</Content>
		</div>
	);
}

export default Home;

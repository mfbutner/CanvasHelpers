import { createContext, useContext, useState } from "react";

const defaultContextValue = {
	data: {
		navOpen: false,
	},
	update: () => {}
};

const globalDataContext = createContext(defaultContextValue);

export function GlobalContext({ children }) {
	const [globals, setGlobals] = useState({ ...defaultContextValue.data });
	const globalValue = {
		data: globals,
		update: newVal => {
			setGlobals(oldVal => {
				return {
					...oldVal,
					...newVal
				};
			});
		}
	};

	return (
		<globalDataContext.Provider value={globalValue}>
			{children}
		</globalDataContext.Provider>
	);
}

export default function useGlobal() {
	return useContext(globalDataContext);
}
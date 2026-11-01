import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { Provider } from "react-redux";
import LandingPage from "./landing-page/LandingPage";
import { store } from "./app/store";
import ContextProvider from "./context/context";

beforeEach(() => {
  window.localStorage.clear();
});

test("renders the Bugs Finder landing page with one navigation bar", () => {
  render(
    <ContextProvider>
      <Provider store={store}>
        <MemoryRouter>
          <LandingPage />
        </MemoryRouter>
      </Provider>
    </ContextProvider>
  );

  expect(
    screen.getByRole("heading", { name: /our bug finder/i })
  ).toBeInTheDocument();
  expect(screen.getAllByRole("banner")).toHaveLength(1);
});

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import AuthPage from "./AuthPage";

describe("AuthPage", () => {
  it("submits valid login credentials", async () => {
    const onSubmit = vi.fn().mockResolvedValue({
      access_token: "access-token",
      token_type: "bearer",
      expires_in: 3600,
      user: { id: "user-1", email: "user@example.com" },
    });
    const { container } = render(<AuthPage onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText("Correo electrónico"), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "long-password" },
    });
    fireEvent.submit(container.querySelector("form")!);

    await waitFor(() => expect(onSubmit).toHaveBeenCalledWith(
      "login",
      "user@example.com",
      "long-password",
    ));
  });

  it("rejects mismatched registration passwords before sending the request", async () => {
    const onSubmit = vi.fn();
    const { container } = render(<AuthPage onSubmit={onSubmit} />);
    fireEvent.click(screen.getByRole("button", { name: "Crear cuenta" }));
    fireEvent.change(screen.getByLabelText("Correo electrónico"), {
      target: { value: "user@example.com" },
    });
    fireEvent.change(screen.getByLabelText("Contraseña"), {
      target: { value: "long-password" },
    });
    fireEvent.change(screen.getByLabelText("Confirma tu contraseña"), {
      target: { value: "different-password" },
    });
    fireEvent.submit(container.querySelector("form")!);

    expect(await screen.findByRole("alert")).toHaveTextContent("Las contraseñas no coinciden.");
    expect(onSubmit).not.toHaveBeenCalled();
  });
});

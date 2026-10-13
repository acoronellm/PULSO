import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import HealthForm from "../HealthForm";

describe("HealthForm", () => {
  it("renderiza los campos principales del formulario", () => {
    render(<HealthForm onSubmit={vi.fn()} loading={false} />);

    expect(
      screen.getByRole("heading", {
        name: /conoce tu perfil cardiovascular/i,
      })
    ).toBeInTheDocument();

    expect(screen.getByLabelText(/sexo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/edad/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/altura/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/peso/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/presión sistólica/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/presión diastólica/i)).toBeInTheDocument();
  });

  it("muestra error si la presión sistólica no es mayor que la diastólica", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<HealthForm onSubmit={onSubmit} loading={false} />);

    await user.type(screen.getByLabelText(/edad/i), "45");
    await user.type(screen.getByLabelText(/altura/i), "170");
    await user.type(screen.getByLabelText(/peso/i), "70");
    await user.type(screen.getByLabelText(/presión sistólica/i), "80");
    await user.type(screen.getByLabelText(/presión diastólica/i), "90");

    await user.click(
      screen.getByRole("button", {
        name: /analizar mi perfil/i,
      })
    );

    expect(
      screen.getByText(
        /la presión sistólica debe ser mayor que la presión diastólica/i
      )
    ).toBeInTheDocument();

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("envía el payload correcto y calcula el BMI", async () => {
    const user = userEvent.setup();
    const onSubmit = vi.fn();

    render(<HealthForm onSubmit={onSubmit} loading={false} />);

    await user.type(screen.getByLabelText(/edad/i), "45");
    await user.type(screen.getByLabelText(/altura/i), "170");
    await user.type(screen.getByLabelText(/peso/i), "70");
    await user.type(screen.getByLabelText(/presión sistólica/i), "120");
    await user.type(screen.getByLabelText(/presión diastólica/i), "80");

    await user.click(
      screen.getByRole("button", {
        name: /analizar mi perfil/i,
      })
    );

    expect(onSubmit).toHaveBeenCalledTimes(1);

    expect(onSubmit).toHaveBeenCalledWith({
      gender: 1,
      height: 170,
      weight: 70,
      ap_hi: 120,
      ap_lo: 80,
      smoke: 0,
      alco: 0,
      active: 1,
      age_years: 45,
      bmi: 24.22,
    });
  });

  it("deshabilita el botón cuando loading es true", () => {
    render(<HealthForm onSubmit={vi.fn()} loading={true} />);

    const button = screen.getByRole("button", {
      name: /analizando/i,
    });

    expect(button).toBeDisabled();
  });
});
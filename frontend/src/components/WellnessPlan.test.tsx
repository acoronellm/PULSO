
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import WellnessPlan from "./WellnessPlan";

describe("WellnessPlan", () => {
  it("muestra solamente ejercicios y medición de presión", () => {
    const onTabChange = vi.fn();

    render(
      <WellnessPlan
        activeTab="ejercicios"
        onTabChange={onTabChange}
      />,
    );

    expect(screen.getAllByRole("tab")).toHaveLength(2);
    expect(screen.getByRole("tab", { name: /Ejercicios/i })).toBeTruthy();
    expect(screen.getByRole("tab", { name: /Medir mi presión/i })).toBeTruthy();
    expect(screen.queryByRole("tab", { name: /Recetas/i })).toBeNull();

    fireEvent.click(screen.getByRole("tab", { name: /Medir mi presión/i }));

    expect(onTabChange).toHaveBeenCalledWith("medir");
  });

  it("conserva las instrucciones de medición de presión", () => {
    render(
      <WellnessPlan activeTab="medir" onTabChange={vi.fn()} />,
    );

    expect(screen.getByText(/Reposa 5 minutos sentado/i)).toBeTruthy();
    expect(screen.getByText(/Brazo a la altura del corazón/i)).toBeTruthy();
    expect(screen.getByText(/Dos tomas con 1 min de pausa/i)).toBeTruthy();
  });
});

// Small live validation helper used on public and admin forms.
// It checks required fields, length, email, phone, date, rating, image type, and image size while the user types.
(function () {
  const imageTypes = ["image/jpeg", "image/png", "image/gif", "image/webp"];

  function labelFor(field) {
    const label = field.closest("div")?.querySelector("label");
    return label ? label.textContent.replace("*", "").trim() : field.name || "This field";
  }

  function errorNode(field) {
    let node = field.parentElement.querySelector("[data-live-error]");
    if (!node) {
      node = document.createElement("p");
      node.className = "field-error";
      node.setAttribute("data-live-error", "true");
      field.insertAdjacentElement("afterend", node);
    }
    return node;
  }

  function fileSizeMb(field) {
    return Number(field.dataset.maxSizeMb || "16");
  }

  function messageFor(field) {
    const value = (field.value || "").trim();
    const name = labelFor(field);

    if (field.type === "file") {
      const files = Array.from(field.files || []);
      if (field.required && files.length === 0) return `${name} is required.`;
      if (files.length === 0) return "";
      if (files.some((file) => !imageTypes.includes(file.type))) return "Please choose only JPG, PNG, GIF, or WebP images.";
      if (files.some((file) => file.size > fileSizeMb(field) * 1024 * 1024)) return `Each image must be smaller than ${fileSizeMb(field)} MB.`;
      return "";
    }

    if (field.type === "radio") {
      const group = field.form.querySelectorAll(`input[type="radio"][name="${field.name}"]`);
      if (field.required && !Array.from(group).some((item) => item.checked)) return `${name} is required.`;
      return "";
    }

    if (field.required && !value) return `${name} is required.`;
    if (!value) return "";
    if (field.minLength > 0 && value.length < field.minLength) return `${name} must be at least ${field.minLength} characters.`;
    if (field.maxLength > 0 && value.length > field.maxLength) return `${name} must be ${field.maxLength} characters or less.`;
    if (field.type === "email" && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return "Please enter a valid email address.";
    if (field.dataset.phone === "true" && !/^[0-9+()\s-]{7,20}$/.test(value)) return "Phone number can only use digits and + - ( ) symbols.";
    if (field.type === "date" && Number.isNaN(Date.parse(value))) return "Please choose a valid date.";
    if (field.pattern && !new RegExp(`^(?:${field.pattern})$`).test(value)) return field.title || `${name} is not valid.`;
    return "";
  }

  function validateField(field) {
    if (field.disabled || field.type === "hidden" || field.closest("[data-skip-live-validation]")) return true;
    const message = messageFor(field);
    const node = errorNode(field);
    field.classList.toggle("is-invalid", Boolean(message));
    field.setAttribute("aria-invalid", message ? "true" : "false");
    node.textContent = message;
    node.hidden = !message;
    return !message;
  }

  function fieldsFor(form) {
    return Array.from(form.querySelectorAll("input, textarea, select")).filter((field) => field.type !== "hidden");
  }

  document.querySelectorAll("form[data-live-validate]").forEach((form) => {
    form.setAttribute("novalidate", "novalidate");

    fieldsFor(form).forEach((field) => {
      const eventName = field.type === "file" || field.type === "radio" || field.tagName === "SELECT" ? "change" : "input";
      field.addEventListener(eventName, () => validateField(field));
      field.addEventListener("blur", () => validateField(field));
    });

    form.addEventListener("submit", (event) => {
      const valid = fieldsFor(form).map(validateField).every(Boolean);
      if (!valid) {
        event.preventDefault();
        const firstError = form.querySelector(".is-invalid");
        if (firstError) firstError.focus();
      }
    });
  });
})();

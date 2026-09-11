(() => {
  const mobileViewport = window.matchMedia("(max-width: 47.999rem)");

  function setSidebarState(isOpen) {
    const sidebar = document.getElementById("R-sidebar");
    const trigger = document.querySelector(".topbar-button-sidebar button");

    if (trigger) {
      trigger.setAttribute("aria-controls", "R-sidebar");
      trigger.setAttribute("aria-expanded", String(mobileViewport.matches && isOpen));
    }

    if (!sidebar) {
      return;
    }

    if (mobileViewport.matches && !isOpen) {
      sidebar.setAttribute("aria-hidden", "true");
      sidebar.inert = true;
    } else {
      sidebar.removeAttribute("aria-hidden");
      sidebar.inert = false;
    }
  }

  function setTopbarFlyoutState(button, isOpen) {
    if (!button) {
      return;
    }

    const trigger = button.querySelector("button");
    const content = button.querySelector(":scope > .topbar-content");
    if (!trigger || !content) {
      return;
    }

    if (!content.id) {
      content.id = `R-${[...button.classList]
        .find((className) => className.startsWith("topbar-button-"))
        ?.replace("topbar-button-", "topbar-flyout-")}`;
    }

    trigger.setAttribute("aria-controls", content.id);
    trigger.setAttribute("aria-expanded", String(isOpen));
  }

  function initialiseAccessibility() {
    const sidebar = document.getElementById("R-sidebar");
    if (!sidebar) {
      return;
    }

    const openNav = window.openNav;
    const closeNav = window.closeNav;
    const openTopbarButtonFlyout = window.openTopbarButtonFlyout;
    const closeTopbarButtonFlyout = window.closeTopbarButtonFlyout;

    setSidebarState(document.body.classList.contains("sidebar-flyout"));
    document
      .querySelectorAll(".topbar-button-toc, .topbar-button-more")
      .forEach((button) => setTopbarFlyoutState(button, button.classList.contains("topbar-flyout")));

    if (typeof openNav === "function") {
      window.openNav = function () {
        setSidebarState(true);
        return openNav.apply(this, arguments);
      };
    }

    if (typeof closeNav === "function") {
      window.closeNav = function () {
        const result = closeNav.apply(this, arguments);
        setSidebarState(false);
        return result;
      };
    }

    if (typeof openTopbarButtonFlyout === "function") {
      window.openTopbarButtonFlyout = function (button) {
        setTopbarFlyoutState(button, true);
        return openTopbarButtonFlyout.apply(this, arguments);
      };
    }

    if (typeof closeTopbarButtonFlyout === "function") {
      window.closeTopbarButtonFlyout = function (button) {
        const result = closeTopbarButtonFlyout.apply(this, arguments);
        setTopbarFlyoutState(button, false);
        return result;
      };
    }

    mobileViewport.addEventListener("change", () => {
      setSidebarState(document.body.classList.contains("sidebar-flyout"));
    });
  }

  window.addEventListener("DOMContentLoaded", initialiseAccessibility);
})();

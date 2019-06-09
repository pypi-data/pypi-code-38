
THEME = {

    "--mdc-theme-primary": "#3f51b5 !important",
    "--mdc-theme-primary-light": "#a4addf !important",
    "--mdc-theme-primary-dark": "#6f7dcd !important",

    "--mdc-theme-secondary": "#ff4081 !important",
    "--mdc-theme-secondary-light": "#ff87b0 !important",
    "--mdc-theme-secondary-dark": "#f80054 !important",

    "--mdc-theme-background": "#fff !important",

    "--mdc-theme-text-primary-on-primary": "#fff !important",
    "--mdc-theme-text-primary-on-primary-dark": "#fff !important",

    "--mdc-theme-text-primary-on-secondary": "#fff !important",
    "--mdc-theme-text-primary-on-secondary-dark": "#fff !important",

    "--mdc-theme-text-primary-on-dark": "#fff !important",

    "--mdc-theme-text-secondary-on-primary": "hsla(0,0%,100%,.7) !important",
    "--mdc-theme-text-hint-on-primary": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-disabled-on-primary": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-icon-on-primary": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-primary-on-primary-light": "rgba(0,0,0,.87) !important",
    "--mdc-theme-text-secondary-on-primary-light": "rgba(0,0,0,.54) !important",
    "--mdc-theme-text-hint-on-primary-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-disabled-on-primary-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-icon-on-primary-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-secondary-on-primary-dark": "hsla(0,0%,100%,.7) !important",
    "--mdc-theme-text-hint-on-primary-dark": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-disabled-on-primary-dark": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-icon-on-primary-dark": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-secondary-on-secondary": "hsla(0,0%,100%,.7) !important",
    "--mdc-theme-text-hint-on-secondary": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-disabled-on-secondary": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-icon-on-secondary": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-primary-on-secondary-light": "rgba(0,0,0,.87) !important",
    "--mdc-theme-text-secondary-on-secondary-light": "rgba(0,0,0,.54) !important",
    "--mdc-theme-text-hint-on-secondary-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-disabled-on-secondary-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-icon-on-secondary-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-secondary-on-secondary-dark": "hsla(0,0%,100%,.7) !important",
    "--mdc-theme-text-hint-on-secondary-dark": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-disabled-on-secondary-dark": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-icon-on-secondary-dark": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-primary-on-background": "rgba(0,0,0,.87) !important",
    "--mdc-theme-text-secondary-on-background": "rgba(0,0,0,.54) !important",
    "--mdc-theme-text-hint-on-background": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-disabled-on-background": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-icon-on-background": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-primary-on-light": "rgba(0,0,0,.87) !important",
    "--mdc-theme-text-secondary-on-light": "rgba(0,0,0,.54) !important",
    "--mdc-theme-text-hint-on-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-disabled-on-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-icon-on-light": "rgba(0,0,0,.38) !important",
    "--mdc-theme-text-secondary-on-dark": "hsla(0,0%,100%,.7) !important",
    "--mdc-theme-text-hint-on-dark": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-disabled-on-dark": "hsla(0,0%,100%,.5) !important",
    "--mdc-theme-text-icon-on-dark": "hsla(0,0%,100%,.5) !important",


    '--mdc-theme-surface': '#fff !important',
    '--mdc-theme-error': '#b00020 !important',
    '--mdc-theme-on-primary': '#fff !important',
    "--mdc-theme-on-secondary": '#ff0000 !important',
    '--mdc-theme-on-surface': '#000 !important',
    '--mdc-theme-on-error': '#fff !important',



}


CSS = """



.mdc-icon-toggle--primary:after, .mdc-icon-toggle--primary:before {
    background-color: rgba(var(--var-theme-primary), 0.14) !important;
    opacity: 0 !important;
}

//.mdc-icon-toggle--secondary:after, .mdc-icon-toggle--secondary:before {
//    background-color: rgba(var(--var-theme-secondary), 0.14) !important;
//    opacity: 0 !important;
//}


.mdc-button:after, .mdc-button:before {
    background-color: rgba(var(--var-theme-primary), 0.16) !important;
    opacity: 0 !important;
}


.mdc-text-field--focused:not(.mdc-text-field--disabled) .mdc-floating-label {
    color: rgba(var(--var-theme-secondary), 1) !important;
}


::placeholder {
    color:  rgba(var(--var-theme-secondary), 1) !important;
}



::-webkit-scrollbar {
    display: none;
}


.mdc-list-item--selected .mdc-list-item__graphic,
.mdc-list-item--activated .mdc-list-item__graphic,
.mdc-list-item--selected, .mdc-list-item--activated {
    color: var(--mdc-theme-secondary, 1) !important;
}


"""

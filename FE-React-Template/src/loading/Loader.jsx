import styles from "./Loader.module.css";

const Loader = () => {
  return (
    <div className={styles.overlay}>
      <div className={styles.loaderContainer}>
        <div className={styles.container}>
          <div className={styles.dot}></div>
          <div className={styles.dot}></div>
          <div className={styles.dot}></div>
          <div className={styles.dot}></div>
          <div className={styles.dot}></div>
        </div>

        <svg width="0" height="0" className={styles.svg}>
          <defs>
            <filter id="uib-jelly-ooze">
              <feGaussianBlur in="SourceGraphic" stdDeviation="3" result="blur" />
              <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="ooze" />
              <feBlend in="SourceGraphic" in2="ooze" />
            </filter>
          </defs>
        </svg>
      </div>
    </div>
  );
};

export default Loader;

import type { ReactNode } from 'react'
import styles from './ReportColumn.module.css'

interface ReportColumnProps<T extends { key: string }> {
  title: string
  items: T[]
  emptyMessage: string
  renderItem: (item: T) => ReactNode
}

export function ReportColumn<T extends { key: string }>({
  title,
  items,
  emptyMessage,
  renderItem,
}: ReportColumnProps<T>) {
  return (
    <section className={styles.column}>
      <header className={styles.plate}>
        <h2 className={styles.title}>{title}</h2>
        <span className={styles.count}>{items.length}</span>
      </header>
      {items.length === 0 ? (
        <p className={styles.empty}>{emptyMessage}</p>
      ) : (
        <ul className={styles.list}>
          {items.map((item) => (
            <li key={item.key}>{renderItem(item)}</li>
          ))}
        </ul>
      )}
    </section>
  )
}

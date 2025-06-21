
import Button from '@/components/Button'
import formatDate from '@/utils/formatDate'
import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'

function HomePage() {
  const { t } = useTranslation()
  const [formattedDate, setFormattedDate] = useState<string>('')

  useEffect(() => {
    const currentDate = new Date()
    const dateStr = formatDate(currentDate)
    setFormattedDate(dateStr)
  }, [])

  const handleClick = () => {
    alert(t('Button がクリックされた!'))
  }

  return (
    <div>
      <h1>{t('Welcome to the Home Page')} - {formattedDate}</h1>
      <Button label={t('Click Me')} onClick={handleClick} />
    </div>
  )
}

export default HomePage


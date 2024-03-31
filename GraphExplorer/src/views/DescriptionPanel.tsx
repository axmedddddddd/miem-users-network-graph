import React from 'react';
// Importing icon components from 'react-icons'
import { BsInfoCircle } from 'react-icons/bs';
// Importing Panel component from a relative path
import Panel from './Panel';

const DescriptionPanel = () => (
  <Panel initiallyDeployed title={<BsInfoCircle className="text-muted"> Обзор</BsInfoCircle>}>
    <h1>Граф пользователей МИЭМ</h1>
    <p>Интерактивное визуальное представление проектной активности участников МИЭМ</p>
    <ProjectSource />
    <WorkingPrinciple />
    <DataAccess />
  </Panel>
);

// Extract Project Source Information as a separate component for better readability
// Extract Project Source Information as a separate component for better readability
function ProjectSource() {
  return (
    <>
      <p>
        Исходный код: <a href="https://git.miem.hse.ru/1731/miem_users_network_graph">GitLab</a>
      </p>
      <p>
        Разработчик: <a href="mailto:amarbuliev@edu.hse.ru">amarbuliev@edu.hse.ru</a>
      </p>
      {/* Removed or adjusted the paragraph that adds extra spacing for minimal space */}
    </>
  );
}

// Extract How It Works section into a separate component for modularity and maintainability
function WorkingPrinciple() {
  return (
    <>
      <h2>Как это работает?</h2>
      <p>Данные активных проектов МИЭМ извлекаются из <a href="https://cabinet.miem.hse.ru/public-api">API кабинета</a></p>
      <p>Граф строится на основе этих данных, представляя:</p>
      <ul>
        <li><strong>Узлы</strong> - это участники проектов, включая как руководителей проектов, так и исполнителей</li>
        <li><strong>Связи</strong> - создается связь между двумя участниками, если они работают в рамках одного проекта</li>
      </ul>
    </>
  );
}

// Extract Data Access section into a separate component for better organization
function DataAccess() {
  return (
    <>
      <h2>Доступ к данным</h2>
      <p>Данные, используемые для построения графа, хранятся в нашем аналитическом хранилище ClickHouse в схеме sandbox, в таблице ongoing_projects</p>
    </>
  );
}

export default DescriptionPanel;

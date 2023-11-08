import React, { FC } from "react";
import { BsInfoCircle } from "react-icons/bs";

import Panel from "./Panel";

const DescriptionPanel: FC = () => {
  return (
    <Panel
      initiallyDeployed
      title={
        <>
          <BsInfoCircle className="text-muted" /> Описание
        </>
      }
    >
      <p>
        <h1>Граф пользователей МИЭМ</h1>

        <p>Визуальное представление участников проектной деятельности МИЭМ.</p>

        <p><mark>Исходный код</mark> - <a href="https://git.miem.hse.ru/400/miem-users-network">GitLab</a></p>
        <p><mark>Разрабочик</mark> - aesaparov@edu.hse.ru</p>

        <h2>Описание работы</h2>

        <p>Из <a href="https://devcabinet.miem.vmnet.top/api/doc">API</a> кабинета МИЭМ берутся данные о текущах, т.е.
          активных,
          проектах.
        </p>

        <h3>Построение графа</h3>

        <p>По собранной информации строится граф, в котором</p>
        <p>
          <ul>
            <li><strong>вершины</strong> - участники проектной деятельности (как руководители проектов, так и
              непосредственно исполнители)</li>
            <li><strong>связи</strong> между вершинами задаются если два человека числятся в одном проекте</li>
          </ul>
        </p>

        <h2>Доступ к API</h2>

        <p>Публичного доступа к API формирования графа сейчас нет, но можно клонировать
          <a href="https://git.miem.hse.ru/400/miem-users-network">репозиторий</a> и воспользоваться исходным кодом.
        </p>
      </p>
    </Panel>
  );
};

export default DescriptionPanel;
